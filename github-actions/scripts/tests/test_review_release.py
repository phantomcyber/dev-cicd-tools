from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from ..review_release import main as review_release


@pytest.fixture(scope='function', autouse=True, params=['Splunk', 'Other'])
def app_json(request):
    return {
        'appid': '123',
        'app_version': '1.0',
        'publisher': request.param
    }


@pytest.fixture(scope='function')
def app_json_splunk_supported(app_json):
    if app_json['publisher'] != 'Splunk':
        pytest.skip()
    return app_json


@pytest.fixture(scope='function', autouse=True)
def get_app_json(mocker, app_json):
    mock = mocker.patch('scripts.review_release.main.get_app_json', autospec=True)
    mock.return_value = app_json

    return mock


@pytest.fixture(scope='function')
def github_client(mocker):
    return mocker.patch('github.Github', autospec=True).return_value


@pytest.fixture(scope='function')
def github_repo(github_client):
    repo = MagicMock()
    github_client.get_repo.side_effect = [repo]

    return repo


@pytest.fixture(scope='function')
def commit(github_repo):
    commit = MagicMock()
    github_repo.get_commit.side_effect = [commit]

    return commit


@pytest.fixture(scope='function')
def combined_commit_status(commit):
    combined_status = MagicMock()
    commit.get_combined_status.side_effect = [combined_status]

    return combined_status


def mock_commit_status(status_name, state):
    status = MagicMock()
    status.context = status_name
    status.state = state

    return status


@contextmanager
def mock_splunk_base_data(**kwargs):
    with patch('scripts.review_release.main._get_splunk_base_data') as mock:
        mock.return_value = kwargs
        yield


def test_review_release_auto_approved(github_repo, app_json, combined_commit_status):
    if app_json['publisher'] == 'Splunk':
        pytest.skip()

    mock_statuses = [mock_commit_status(f'AWS CodeBuild us-west-2 ({s})', 'success')
                     for s in review_release.REQUIRED_COMMIT_STATUSES]
    combined_commit_status.statuses = mock_statuses

    with mock_splunk_base_data(support='community'):
        assert review_release.review_release(github_repo, '/local/path', 'ref') == 0


def test_review_release_manual_approval_splunk_supported_app(github_repo, app_json, combined_commit_status):
    if app_json['publisher'] != 'Splunk':
        pytest.skip()

    mock_statuses = [mock_commit_status(f'AWS CodeBuild us-west-2 ({s})', 'success')
                     for s in review_release.REQUIRED_COMMIT_STATUSES]
    combined_commit_status.statuses = mock_statuses

    with mock_splunk_base_data(support='splunk'):
        assert review_release.review_release(github_repo, '/local/path', 'ref') == 1


def test_review_release_manual_approval_missing_commit_statuses(github_repo, app_json, combined_commit_status):
    mock_statuses = [mock_commit_status(f'AWS CodeBuild us-west-2 ({s})', 'success')
                     for s in review_release.REQUIRED_COMMIT_STATUSES[:-1]]
    combined_commit_status.statuses = mock_statuses

    with mock_splunk_base_data(support=app_json['publisher'].lower()):
        assert review_release.review_release(github_repo, '/local/path', 'ref') == 1


def test_review_release_manual_approval_unsuccessful_commit_statuses(github_repo, app_json, combined_commit_status):
    mock_statuses = [mock_commit_status(f'AWS CodeBuild us-west-2 ({s})', 'failed')
                     for s in review_release.REQUIRED_COMMIT_STATUSES]
    combined_commit_status.statuses = mock_statuses

    with mock_splunk_base_data(support=app_json['publisher'].lower()):
        assert review_release.review_release(github_repo, '/local/path', 'ref') == 1


def test_review_release_manual_approval_support_status_change(github_repo, app_json, combined_commit_status):
    mock_statuses = [mock_commit_status(f'AWS CodeBuild us-west-2 ({s})', 'success')
                     for s in review_release.REQUIRED_COMMIT_STATUSES]
    combined_commit_status.statuses = mock_statuses

    support_tag = 'community' if app_json['publisher'] == 'Splunk' else 'splunk'
    with mock_splunk_base_data(support=support_tag):
        assert review_release.review_release(github_repo, '/local/path', 'ref') == 1
