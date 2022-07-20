import datetime
import os

import pytest

from generate_release_notes import generate_release_notes, RELEASE_NOTES_DATE_FORMAT
from tests import copy_app_dir

APP_NAME = 'App'
APP_VERSION = '1.0'
PUBLISHER = 'Splunk'
PUBLISH_DATE = datetime.date.today().strftime(RELEASE_NOTES_DATE_FORMAT)


@pytest.fixture(scope='function')
def app_json():
    return {
        'app_version': APP_VERSION,
        'name': APP_NAME,
        'publisher': PUBLISHER
    }


@pytest.fixture(scope='function', params=[
    'tests/data/release_notes/existing_release_notes',
    'tests/data/release_notes/missing_release_notes',
    'tests/data/release_notes/nested_notes',
    'tests/data/release_notes/existing_release_notes_md'
])
def app_dir(request):
    return copy_app_dir(request)


def test_generate_release_notes(app_dir, app_json):
    updates = generate_release_notes(app_dir, APP_VERSION, app_json)

    with open(os.path.join(app_dir, 'release_notes/expected_release_notes.md')) as f:
        assert updates[f'release_notes/{APP_VERSION}.md'] == f.read()


@pytest.fixture(scope='function', params=[
    'tests/data/release_notes/invalid_unreleased_md',
    'tests/data/release_notes/invalid_unreleased_md_nested'
])
def app_dir_invalid(request):
    return copy_app_dir(request)


def test_generate_release_notes_invalid(app_dir_invalid, app_json):
    with pytest.raises(ValueError):
        generate_release_notes(app_dir_invalid, APP_VERSION, app_json)


@pytest.fixture(scope='function', params=[
    'tests/data/release_notes/nothing_to_release'
])
def app_dir_no_release(request):
    return copy_app_dir(request)


def test_generate_release_notes_nothing_to_release(app_dir_no_release, app_json):
    assert {} == generate_release_notes(app_dir_no_release, APP_VERSION, app_json)
