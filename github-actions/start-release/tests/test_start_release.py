import base64
import json
import logging
import datetime
import os
import shutil
import tempfile
from collections import namedtuple
from distutils.version import LooseVersion
from unittest.mock import MagicMock, call, Mock

import pytest
from requests import HTTPError
from http import HTTPStatus

from start_release import start_release, RELEASE_NOTES_DATE_FORMAT, DEFAULT_ENCODING, \
    RELEASE_NOTE_COMMIT_MSG, COMMIT_AUTHOR, load_main_pr_body, MAIN_PR_TITLE, deserialize_app_json, FIRST_VERSION
from tests import copy_app_dir

logging.getLogger().setLevel(logging.INFO)

APP_NAME = 'App'
PUBLISHER = 'Splunk'
COPYRIGHT = 'Copyright (c) Splunk Inc.'
SHA = '59308dba2df36f51e77e6a8b8501c960c7999999'
#SHA_NEXT = '59308dba2df36f51e77e6a8b8501c960c7999999'
#SHA_MAIN = '59308dba2df36f51e77e6a8b8501c960c7888888'
DATE = datetime.date.today().strftime(RELEASE_NOTES_DATE_FORMAT)
NEXT_VERSION_OKAY = '1.0.1'
NEXT_VERSION_TOO_SMALL = '1.0.0'
MAIN_VERSION = '1.0.0'


@pytest.fixture(name='session', scope='function')
def mock_github_api_session(mocker):
    return mocker.patch('api.github.GitHubApiSession', autospec=True).return_value


@pytest.fixture(name='generate_release_notes', scope='function')
def mock_generate_release_notes(mocker):
    return mocker.patch('start_release.generate_release_notes', autospec=True)


@pytest.fixture(name='update_copyrights', scope='function')
def mock_update_copyrights(mocker):
    return mocker.patch('start_release.update_copyrights', autospec=True)


@pytest.fixture(name='build_docs', scope='function')
def mock_build_docs(mocker):
    return mocker.patch('start_release.build_docs_from_html', autospec=True)


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
        'publisher': PUBLISHER,
        'license': COPYRIGHT
    }, indent=4)
    return {
        'content': base64.b64encode(app_json.encode(DEFAULT_ENCODING)),
        'sha': SHA
    }


TestData = namedtuple('TestData', ['unreleased_md',
                                   'expected_release_notes_md'])


@pytest.fixture(scope='function',
                params=[
                    TestData('tests/data/unreleased.md',
                             'tests/data/expected_release_notes.md')
                ])
def test_data(request):
    return request.param


def encode_text_file(file_path):
    if not file_path:
        return None

    with open(file_path) as f:
        return {
            'content': base64.b64encode(f.read().encode(DEFAULT_ENCODING))
        }


@pytest.fixture(scope='function')
def app_dir(request):
    app_dir = tempfile.mkdtemp()
    release_notes_dir = os.path.join(app_dir, 'release_notes')
    os.mkdir(release_notes_dir)
    shutil.copytree('tests/data/release_notes/existing_release_notes', release_notes_dir)

    shutil.copytree('tests/data/copyrights/app_dir', app_dir)
    return copy_app_dir(request)


@pytest.fixture(scope='function', params=[True, False])
def existing_pr(request):
    return request.param


def test_start_release_happy_path(session,
                                  next_version,
                                  main_version,
                                  generate_release_notes,
                                  update_copyrights,
                                  build_docs,
                                  existing_pr):
    base_sha, json_sha, tree_sha, commit_sha = (i for i in range(4))
    session.get = MagicMock()

    app_json_next = mock_app_json(next_version)
    app_json_main = mock_app_json(main_version) if main_version else HTTPError(response=Mock(status_code=404))

    sha_field_next = SHA
    sha_field_main = SHA

    open_prs = [{
        'head': {'ref': 'a'},
        'base': {'ref': 'b'},
        'html_url': 'url'
    }]
    if existing_pr:
        open_prs.append({
            'head': {'ref': 'next'},
            'base': {'ref': 'main'},
            'html_url': 'url'
        })
    if isinstance(app_json_main, dict):
        session.get.side_effect = [
            [{'name': '{}.json'.format(APP_NAME)}, {'name': '{}.postman_collection.json'.format(APP_NAME)}],
            app_json_next,
            app_json_next,
            app_json_main,
            app_json_main,
            {'object': {'sha': base_sha}},
            open_prs
        ]
    else:
        session.get.side_effect = [
            [{'name': '{}.json'.format(APP_NAME)}, {'name': '{}.postman_collection.json'.format(APP_NAME)}],
            app_json_next,
            app_json_next,
            app_json_main,
            {'object': {'sha': base_sha}},
            open_prs
        ]

    main_version = main_version or FIRST_VERSION
    if LooseVersion(next_version) <= LooseVersion(main_version):
        expected_next_version = main_version[:-1] + str(int(main_version[-1]) + 1)
        app_json, indent = deserialize_app_json(app_json_next)
        app_json['app_version'] = expected_next_version

        app_json_next = app_json_next.copy()
        app_json_next['content'] = base64.b64encode(json.dumps(app_json, indent=indent).encode(DEFAULT_ENCODING))

        post_blob_sha_l = [json_sha]
        expected_blobs = [base64.b64decode(app_json_next['content']).decode(DEFAULT_ENCODING)]
        expected_tree = [('{}.json'.format(APP_NAME), json_sha)]
    else:
        expected_next_version = next_version
        post_blob_sha_l = []
        expected_blobs = []
        expected_tree = []

    generate_release_notes.return_value = {'unreleased.md': 'unreleased_content'}
    update_copyrights.return_value = {'connector.py': 'connector_content'}
    build_docs.return_value = {'readme.md': 'readme_content'}

    for file, content in {
        **generate_release_notes.return_value,
        **update_copyrights.return_value,
        **build_docs.return_value
    }.items():
        sha = f'{content}_sha'
        post_blob_sha_l.append(sha)
        expected_blobs.append(content)
        expected_tree.append((file, sha))

    post_blob_sha_l.extend([tree_sha, commit_sha])

    session.post = MagicMock()
    post_l = [{'sha': s} for s in post_blob_sha_l]
    if not existing_pr:
        post_l.append({'html_url': 'pr_url'})
    session.post.side_effect = post_l

    start_release(session)

    if isinstance(app_json_main, dict):
        assert session.get.call_count == 7
        assert session.get.call_args_list[0] == call('contents?ref=next')
        assert session.get.call_args_list[1] == call('contents/{}.json?ref=next'.format(APP_NAME))
        assert session.get.call_args_list[2] == call('git/blobs/{}?ref=next'.format(sha_field_next))
        assert session.get.call_args_list[3] == call('contents/{}.json?ref=main'.format(APP_NAME))
        assert session.get.call_args_list[4] == call('git/blobs/{}?ref=main'.format(sha_field_main))
        assert session.get.call_args_list[5] == call('git/ref/heads/next')
        assert session.get.call_args_list[6] == call('pulls')
    else:
        assert session.get.call_count == 6
        assert session.get.call_args_list[0] == call('contents?ref=next')
        assert session.get.call_args_list[1] == call('contents/{}.json?ref=next'.format(APP_NAME))
        assert session.get.call_args_list[2] == call('git/blobs/{}?ref=next'.format(sha_field_next))
        assert session.get.call_args_list[3] == call('contents/{}.json?ref=main'.format(APP_NAME))
        assert session.get.call_args_list[4] == call('git/ref/heads/next')
        assert session.get.call_args_list[5] == call('pulls')

    assert session.post.call_count == len(post_l)

    for i, blob in enumerate(expected_blobs):
        assert session.post.call_args_list[i] == call('git/blobs', content=blob, encoding=DEFAULT_ENCODING)

    post_idx = len(expected_blobs)
    expected_tree = [{'mode': '100644', 'type': 'blob', 'path': path, 'sha': sha}
                     for path, sha in expected_tree]
    assert session.post.call_args_list[post_idx] == call('git/trees', tree=expected_tree, base_tree=base_sha)
    post_idx += 1

    assert session.post.call_args_list[post_idx] == call('git/commits',
                                                         tree=tree_sha, parents=[base_sha],
                                                         message=RELEASE_NOTE_COMMIT_MSG.format(expected_next_version),
                                                         author=COMMIT_AUTHOR)
    post_idx += 1
    if not existing_pr:
        assert session.post.call_args_list[-1] == call('pulls', head='next', base='main',
                                                       body=load_main_pr_body(),
                                                       title=MAIN_PR_TITLE.format(expected_next_version),
                                                       maintainers_can_modify=True)
    assert session.patch.call_count == 1
    assert session.patch.call_args_list[0] == call('git/refs/heads/next', sha=commit_sha)


zero_json_files = []
multiple_json_files = [{'name': f} for f in ('x.json', 'y.json')]


@pytest.fixture(scope='function', name='session_invalid_data',
                params=[[zero_json_files], [multiple_json_files]])
def _session_invalid_data(session, request):
    session.get = MagicMock()
    session.get.side_effect = request.param
    return session


def test_start_release_invalid_data(session_invalid_data):
    with pytest.raises(ValueError):
        start_release(session_invalid_data)

    assert session_invalid_data.post.call_count == 0
    assert session_invalid_data.patch.call_count == 0
