import base64
import json
import logging
import os
import re
from http import HTTPStatus

from distutils.version import LooseVersion

from requests import HTTPError

from api.github import GitHubApiSession
from build_docs import build_docs_from_html
from copyright_updates import update_copyrights
from generate_release_notes import generate_release_notes

RELEASE_NOTES_DIR = 'release_notes'
UNRELEASED_MD = '{}/unreleased.md'.format(RELEASE_NOTES_DIR)
UNRELEASED_MD_HEADER = '**Unreleased**'
RELEASE_NOTES_MD = RELEASE_NOTES_DIR + '/{}.md'
RELEASE_NOTES_TOP_HEADER = '**{} Release Notes - Published by {} {}**\n\n'
RELEASE_NOTES_VERSION_HEADER = '**Version {} - Released {}**\n'
RELEASE_NOTES_DATE_FORMAT = '%B %d, %Y'
RELEASE_NOTE_PATTERN = re.compile(r'^\s*\* (?P<note>.+)$')

# The minimum number of white spaces a nested list entry needs to be
# indented from its parent for it be rendered correctly on GitHub
MD_NESTED_LIST_MIN_INDENT = 2

# The maximum number of white spaces a nested list entry can be
# indented from its parent for it to be rendered correctly on GitHub
MD_NESTED_LIST_MAX_INDENT = 5

DEFAULT_ENCODING = 'utf-8'

RELEASE_NOTE_COMMIT_MSG = 'Release notes for version {}'
MAIN_PR_TITLE = 'Merging next to main for release {}'
MAIN_PR_BODY_FILE = 'templates/main_pr_body.md'
COMMIT_AUTHOR = {
    'name': 'root',
    'email': 'root@splunksoar'
}

FIRST_VERSION = '1.0.0'


def deserialize_app_json(app_json):
    json_str = base64.b64decode(app_json['content']).decode(DEFAULT_ENCODING)
    start = idx = json_str.find('\n') + 2
    while json_str[idx] != '"':
        idx += 1
    indent = idx - start + 1

    return json.loads(json_str), indent


def deserialize_text_file(unreleased_md):
    return base64.b64decode(unreleased_md['content'])\
        .decode(DEFAULT_ENCODING).split('\n')


def load_main_pr_body():
    with open(MAIN_PR_BODY_FILE) as f:
        return f.read()


def _handle_http_not_found(ex):
    if not isinstance(ex, HTTPError) or ex.response.status_code != HTTPStatus.NOT_FOUND:
        raise ex


def start_release(session, app_dir=os.getenv('GITHUB_WORKSPACE')):
    # Fetch repo contents and find the app json file - which we
    # expect to be the only json file other than a potential postman collection
    repo_files = session.get('contents?ref=next')
    json_files = [f['name'] for f in repo_files if
                  not f['name'].lower().endswith('.postman_collection.json')
                  and f['name'].lower().endswith('.json')]

    if len(json_files) != 1:
        raise ValueError('Expected a single json file in the repo but got {}'.format(json_files))

    # Fetch the app json from main branch, and compare the app version
    # to the app version in next. Update the next version to be greater than
    # greater than main, if it already isn't.
    app_json_file = json_files[-1]

    sha_field = session.get('contents/{}?ref=next'.format(app_json_file))['sha']
    app_json_next, app_json_indent = deserialize_app_json(session.get('git/blobs/{}?ref=next'.format(sha_field)))
    app_version_next = app_json_next['app_version']

    try:
        sha_field = session.get('contents/{}?ref=main'.format(app_json_file))['sha']
        app_json_main, _ = deserialize_app_json(session.get('git/blobs/{}?ref=main'.format(sha_field)))
        app_version_main = app_json_main['app_version']
    except HTTPError as ex:
        _handle_http_not_found(ex)
        app_version_main = FIRST_VERSION

    updates = {}
    if LooseVersion(app_version_next) <= LooseVersion(app_version_main):
        logging.warning('Detected the app version in next %s to be <= the app version in main %s',
                        app_version_next, app_version_main)

        app_json_next['app_version'] = app_version_next = app_version_main[:-1] + str(int(app_version_main[-1]) + 1)
        logging.info('Updated the app version in next to be %s', app_version_next)
        updates[app_json_file] = json.dumps(app_json_next, indent=app_json_indent)

    # Generate release notes
    release_note_updates = generate_release_notes(app_dir, app_version_next, app_json_next)
    updates.update(release_note_updates)

    # Update copyright on source files
    app_json_copyright = app_json_next.get('license')
    if app_json_copyright:
        cp_updates = update_copyrights(app_dir, app_json_copyright)
        updates.update(cp_updates)
    else:
        logging.warning('Could not find copyright information in the app JSON!')

    # Generate documentation for the app
    docs_updates = build_docs_from_html(app_dir, app_version_next)
    updates.update(docs_updates)

    # Build a commit from the head of next including the version and
    # release note updates
    tree = []
    for path, content in updates.items():
        tree.append({
            'sha': session.post('git/blobs',
                                content=content,
                                encoding=DEFAULT_ENCODING)['sha'],
            'path': path,
            'mode': '100644',
            'type': 'blob'
            })

    if tree:
        latest_commit_next = session.get('git/ref/heads/next')['object']['sha']
        tree = session.post('git/trees', tree=tree, base_tree=latest_commit_next)
        commit = session.post('git/commits',
                              tree=tree['sha'],
                              parents=[latest_commit_next],
                              message=RELEASE_NOTE_COMMIT_MSG.format(app_version_next),
                              author=COMMIT_AUTHOR)
        logging.info('Created commit %s', commit['sha'])

        # Commit changes to next, we fail at this step if we're
        # unable to do a fast-forward merge, which would mean there
        # were new commit(s) to next since when we checked.
        session.patch('git/refs/heads/next', sha=commit['sha'])
        logging.info('Committed changes to next')

    # Submit a PR to merge next to main if one doesn't exist
    open_prs, next_to_main_pr = session.get('pulls'), None
    for pr in open_prs:
        if pr['head']['ref'] == 'next' and pr['base']['ref'] == 'main':
            next_to_main_pr = pr
            break

    if next_to_main_pr:
        logging.info('PR merging next --> main already exists at: %s', next_to_main_pr['html_url'])
    else:
        pr = session.post('pulls',
                          head='next',
                          base='main',
                          body=load_main_pr_body(),
                          title=MAIN_PR_TITLE.format(app_version_next),
                          maintainers_can_modify=True)
        logging.info('PR merging next --> main created at: %s', pr['html_url'])


def main():
    logging.getLogger().setLevel(logging.INFO)
    session = GitHubApiSession(os.getenv('GITHUB_TOKEN'), os.getenv('APP_REPO'))
    logging.info(os.getenv('APP_REPO'))
    start_release(session)


if __name__ == '__main__':
    main()
