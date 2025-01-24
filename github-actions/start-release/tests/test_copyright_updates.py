from pathlib import Path

import pytest

from copyright_updates import update_copyrights
from tests import copy_app_dir


app_dir_path = "tests/data/copyrights/app_dir"
expected_app_dir_path = "tests/data/copyrights/expected"
new_copyright = "Copyright (c) 2017-2022 Splunk Inc."


@pytest.fixture(scope="function", params=[app_dir_path])
def app_dir(request):
    return copy_app_dir(request)


def test_copyright_updates(app_dir):
    updates = update_copyrights(app_dir, new_copyright)

    expected_files = ("LICENSE", "example_connector.py", "example_view.html")

    for filename in expected_files:
        try:
            actual = updates[filename]
        except KeyError:
            pytest.fail(f"Missing expected license update for file {filename}")

        expected = Path(expected_app_dir_path, filename)
        assert (
            actual == expected.read_text()
        ), f"License update for file {filename} did not match expectations!"

    assert len(updates) == len(expected_files)
