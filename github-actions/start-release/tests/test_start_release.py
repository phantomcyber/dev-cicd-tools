import base64
import json
import logging
import datetime
from distutils.version import LooseVersion
from unittest.mock import MagicMock, call, Mock

import pytest
from requests import HTTPError

from start_release import start_release, RELEASE_NOTES_DATE_FORMAT, DEFAULT_ENCODING, UNRELEASED_MD_HEADER, \
    RELEASE_NOTE_COMMIT_MSG, COMMIT_AUTHOR, load_main_pr_body, MAIN_PR_TITLE, deserialize_app_json, FIRST_VERSION

logging.getLogger().setLevel(logging.INFO)

APP_NAME = 'App'
PUBLISHER = 'Splunk'
DATE = datetime.date.today().strftime(RELEASE_NOTES_DATE_FORMAT)
NEXT_VERSION_OKAY = '1.0.1'
NEXT_VERSION_TOO_SMALL = '1.0.0'
MAIN_VERSION = '1.0.0'


@pytest.fixture(name='session', scope='function')
def mock_github_api_session(mocker):
    return mocker.patch('api.github.GitHubApiSession', autospec=True).return_value


@pytest.fixture(scope='function', params=[NEXT_VERSION_OKAY, NEXT_VERSION_TOO_SMALL])
def next_version(request):
    return request.param


@pytest.fixture(scope='function', params=[MAIN_VERSION, None])
def main_version(request):
    return request.param


def mock_app_json(version):
    app_json = json.dumps({
        'app_version': version,
        'name': APP_NAME,
        'publisher': PUBLISHER
    }, indent=4)
    return {
        'content': base64.b64encode(app_json.encode(DEFAULT_ENCODING))
    }


def mock_unreleased_md():
    return encode_text_file('tests/data/unreleased.md')


def mock_release_notes_html():
    return encode_text_file('tests/data/old_release_notes.html')


def encode_text_file(file_path):
    with open(file_path) as f:
        return {
            'content': base64.b64encode(f.read().encode(DEFAULT_ENCODING))
        }


@pytest.fixture(scope='function', params=[mock_release_notes_html(), None])
def release_notes(request):
    return request.param


def test_start_release_happy_path(session, next_version, main_version, release_notes):
    base_sha, json_sha, release_note_md_sha, \
        release_note_html_sha, unreleased_sha, tree_sha, commit_sha = (i for i in range(7))
    session.get = MagicMock()

    app_json_next = mock_app_json(next_version)
    app_json_main = mock_app_json(main_version) if main_version else HTTPError(response=Mock(status=404))
    release_notes_result = release_notes if release_notes else HTTPError(response=Mock(status=404))
    session.get.side_effect = [[{'name': '{}.json'.format(APP_NAME)}, {'name': '{}.postman_collection.json'.format(APP_NAME)}],
                               app_json_next, app_json_main,
                               mock_unreleased_md(), release_notes_result, {'object': {'sha': base_sha}}]

    main_version = main_version or FIRST_VERSION
    if LooseVersion(next_version) <= LooseVersion(main_version):
        expected_next_version = main_version[:-1] + str(int(main_version[-1]) + 1)
        app_json, indent = deserialize_app_json(app_json_next)
        app_json['app_version'] = expected_next_version

        app_json_next = app_json_next.copy()
        app_json_next['content'] = base64.b64encode(json.dumps(app_json, indent=indent).encode(DEFAULT_ENCODING))

        post_blob_sha_l = [json_sha, release_note_md_sha, release_note_html_sha, unreleased_sha, tree_sha, commit_sha]
        expected_blobs = [base64.b64decode(app_json_next['content']).decode(DEFAULT_ENCODING)]
        expected_tree = [('{}.json'.format(APP_NAME), json_sha)]
    else:
        expected_next_version = next_version
        post_blob_sha_l = [release_note_md_sha, release_note_html_sha, unreleased_sha, tree_sha, commit_sha]
        expected_blobs = []
        expected_tree = []

    session.post = MagicMock()
    post_l = [{'sha': s} for s in post_blob_sha_l] + [{'html_url': 'url'}]
    session.post.side_effect = post_l

    start_release(session)

    assert session.get.call_count == 6
    assert session.get.call_args_list[0] == call('contents?ref=next')
    assert session.get.call_args_list[1] == call('contents/{}.json?ref=next'.format(APP_NAME))
    assert session.get.call_args_list[2] == call('contents/{}.json?ref=main'.format(APP_NAME))
    assert session.get.call_args_list[3] == call('contents/release_notes/unreleased.md?ref=next')
    assert session.get.call_args_list[4] == call('contents/release_notes/release_notes.html?ref=next')
    assert session.get.call_args_list[5] == call('git/ref/heads/next')

    assert session.post.call_count == len(post_l)
    with open('tests/data/expected_release_notes.md') as f:
        expected_blobs.append(f.read() \
                              .replace('<APP_NAME>', 'App') \
                              .replace('<PUBLISHER>', 'Splunk') \
                              .replace('<PUBLISH_DATE>', DATE) \
                              .replace('<VERSION>', expected_next_version))

    if release_notes:
        with open('tests/data/expected_new_release_notes.html') as f:
            expected_blobs.append(f.read() \
                                  .replace('APP_NAME', 'App') \
                                  .replace('PUBLISHER', 'Splunk') \
                                  .replace('PUBLISH_DATE', DATE) \
                                  .replace('VERSION', expected_next_version))
    else:
        with open('tests/data/expected_new_release_notes_no_history.html') as f:
            expected_blobs.append(f.read() \
                                  .replace('APP_NAME', 'App') \
                                  .replace('PUBLISHER', 'Splunk') \
                                  .replace('PUBLISH_DATE', DATE) \
                                  .replace('VERSION', expected_next_version))

    expected_blobs.append('{}\n'.format(UNRELEASED_MD_HEADER))

    expected_tree.append(('release_notes/{}.md'.format(expected_next_version), release_note_md_sha))
    expected_tree.append(('release_notes/release_notes.html', release_note_html_sha))
    expected_tree.append(('release_notes/unreleased.md', unreleased_sha))

    for i, blob in enumerate(expected_blobs):
        assert session.post.call_args_list[i] == call('git/blobs', content=blob, encoding=DEFAULT_ENCODING)

    expected_tree = [{'mode': '100644', 'type': 'blob', 'path': path, 'sha': sha}
                     for path, sha in expected_tree]

    assert session.post.call_args_list[-3] == call('git/trees', tree=expected_tree, base_tree=base_sha)
    assert session.post.call_args_list[-2] == call('git/commits',
                                                   tree=tree_sha, parents=[base_sha],
                                                   message=RELEASE_NOTE_COMMIT_MSG.format(expected_next_version),
                                                   author=COMMIT_AUTHOR)
    assert session.patch.call_count == 1
    assert session.patch.call_args_list[0] == call('git/refs/heads/next', sha=commit_sha)

    assert session.post.call_args_list[-1] == call('pulls', head='next', base='main',
                                                   body=load_main_pr_body(),
                                                   title=MAIN_PR_TITLE.format(expected_next_version),
                                                   maintainers_can_modify=True)


zero_json_files = []
multiple_json_files = [{'name': f} for f in ('x.json', 'y.json')]


def invalid_unreleased_md():
    with open('tests/data/unreleased.md') as f:
        unreleased_md = f.read().split('\n')
        unreleased_md = '\n'.join(unreleased_md[1:]).encode(DEFAULT_ENCODING)

    return [[{'name': '{}.json'.format(APP_NAME)}], mock_app_json('1.1'), mock_app_json('1.0'),
            {'content': base64.b64encode(unreleased_md)}]


@pytest.fixture(scope='function', name='session_invalid_data',
                params=[[zero_json_files], [multiple_json_files], invalid_unreleased_md()])
def _session_invalid_data(session, request):
    session.get = MagicMock()
    session.get.side_effect = request.param
    return session


def test_start_release_invalid_data(session_invalid_data):
    with pytest.raises(ValueError):
        start_release(session_invalid_data)

    assert session_invalid_data.post.call_count == 0
    assert session_invalid_data.patch.call_count == 0


def test_start_release_nothing_to_release(session):
    session.get = MagicMock()
    empty_unreleased_md = base64.b64encode(UNRELEASED_MD_HEADER.encode(DEFAULT_ENCODING))
    session.get.side_effect = [[{'name': '{}.json'.format(APP_NAME)}], mock_app_json('1.1'), mock_app_json('1.0'),
                               {'content': empty_unreleased_md}, mock_release_notes_html()]

    start_release(session)
    assert session.patch.call_count == 0
    assert session.post.call_count == 1
    assert session.post.call_args_list[0] == call('pulls', head='next', base='main',
                                                  body=load_main_pr_body(),
                                                  title=MAIN_PR_TITLE.format('1.1'),
                                                  maintainers_can_modify=True)
