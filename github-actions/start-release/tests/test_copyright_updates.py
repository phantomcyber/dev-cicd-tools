import os

import pytest

from copyright_updates import update_copyrights
from tests import copy_app_dir


app_dir_path = 'tests/data/copyrights/app_dir'
expected_app_dir_path = 'tests/data/copyrights/expected'
new_copyright = 'Copyright (c) 2017-2022 Splunk Inc.'


@pytest.fixture(scope='function', params=[
    app_dir_path
])
def app_dir(request):
    return copy_app_dir(request)


def test_copyright_updates(app_dir):
    updates = update_copyrights(app_dir, new_copyright)

    assert len(updates) == 3

    for actual, expected_fp in [(updates['LICENSE'], os.path.join(expected_app_dir_path, 'LICENSE')),
                                (updates['example_connector.py'], os.path.join(expected_app_dir_path, 'example_connector.py')),
                                (updates['example_view.html'], os.path.join(expected_app_dir_path, 'example_view.html'))]:
        with open(expected_fp) as expected:
            assert actual == expected.read()
