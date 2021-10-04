import argparse
import base64
import datetime
import json
import logging
import os
import re
from distutils.version import LooseVersion

from requests import HTTPError

from api.github import GitHubApiSession

RELEASE_NOTES_DIR = 'release_notes'
UNRELEASED_MD = '{}/unreleased.md'.format(RELEASE_NOTES_DIR)
UNRELEASED_MD_HEADER = '**Unreleased**'
RELEASE_NOTES_MD = RELEASE_NOTES_DIR + '/{}.md'
RELEASE_NOTES_TOP_HEADER = '**{} Release Notes - Published by {} {}**\n\n'
RELEASE_NOTES_VERSION_HEADER = '**Version {} - Released {}**\n'
RELEASE_NOTES_DATE_FORMAT = '%B %d, %Y'
RELEASE_NOTE_PATTERN = re.compile('^\\* .+$')

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


def deserialize_unreleased_md(unreleased_md):
    return base64.b64decode(unreleased_md['content'])\
        .decode(DEFAULT_ENCODING).split('\n')


def build_release_notes(release_version, unreleased_notes, app_json):
    if unreleased_notes[0] != UNRELEASED_MD_HEADER:
        raise ValueError('Expected the first line of {} to be the header {}'
                         .format(UNRELEASED_MD, UNRELEASED_MD_HEADER))
    elif len(unreleased_notes) == 1:
        return None

    publish_date = datetime.date.today().strftime(RELEASE_NOTES_DATE_FORMAT)
    release_notes = [
        RELEASE_NOTES_TOP_HEADER.format(app_json['name'], app_json['publisher'], publish_date),
        RELEASE_NOTES_VERSION_HEADER.format(release_version, publish_date)
    ]
    for note in unreleased_notes[1:]:
        if not note or not note.strip():
            continue
        match = RELEASE_NOTE_PATTERN.match(note)
        if not match:
            raise ValueError('Detected incorrectly formatted release note: \'{}\''
                             .format(note))
        release_notes.append(match.group())

    return '\n'.join(release_notes)


def load_main_pr_body():
    with open(MAIN_PR_BODY_FILE) as f:
        return f.read()


def start_release(session):
    # Fetch repo contents and find the app json file - which we
    # expect to be the only json file
    repo_files = session.get('contents?ref=next')
    json_files = [f['name'] for f in repo_files if f['name'].lower().endswith('.json')]

    if len(json_files) != 1:
        raise ValueError('Expected a single json file in the repo but got {}'.format(json_files))

    # Fetch the app json from main branch, and compare the app version
    # to to app version in next. Update the next version to be greater than
    # greater than main, if it already isn't.
    app_json_file = json_files[-1]
    app_json_next, app_json_indent = deserialize_app_json(session.get('contents/{}?ref=next'.format(app_json_file)))
    app_version_next = app_json_next['app_version']

    try:
        app_json_main, _ = deserialize_app_json(session.get('contents/{}?ref=main'.format(app_json_file)))
        app_version_main = app_json_main['app_version']
    except HTTPError as ex:
        if ex.response.status != 404:
            raise ex
        app_version_main = FIRST_VERSION

    if LooseVersion(app_version_next) <= LooseVersion(app_version_main):
        logging.warning('Detected the app version in next %s to be <= the app version in main %s',
                        app_version_next, app_version_main)

        app_json_next['app_version'] = app_version_next = app_version_main[:-1] + str(int(app_version_main[-1]) + 1)
        logging.info('Updated the app version in next to be %s', app_version_next)

    # Generate release notes for the new app version from the entries
    # in unreleased.md, then truncate unreleased.md
    unreleased_notes = deserialize_unreleased_md(
        session.get('contents/{}?ref=next'.format(UNRELEASED_MD)))

    release_notes = build_release_notes(app_version_next, unreleased_notes, app_json_next)
    unreleased_notes = UNRELEASED_MD_HEADER + '\n'

    if not release_notes:
        logging.info('%s is empty! Assuming there is nothing to release.', release_notes)
        return
    logging.info('Generated release notes for version %s:', app_version_next)
    logging.info(release_notes)

    # Build a commit from the head of next including the version and
    # release note updates
    tree = []
    for content, path in ((json.dumps(app_json_next, indent=app_json_indent), app_json_file),
                          (release_notes, RELEASE_NOTES_MD.format(app_version_next)),
                          (unreleased_notes, UNRELEASED_MD)):
        tree.append({
            'sha': session.post('git/blobs',
                                content=content,
                                encoding=DEFAULT_ENCODING)['sha'],
            'path': path,
            'mode': '100644',
            'type': 'blob'
            })

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

    # Submit a PR to merge next to main
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
