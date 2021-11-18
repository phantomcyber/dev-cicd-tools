import json
import os
import shutil

import pytest

from pathlib import Path
from readme_to_markdown import (readme_html_to_markdown,
    README_MD_ORIGINAL_NAME, README_MD_NAME)


START_RELEASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

TEST_DATA = [
    ("tests/data/readme_to_markdown/has_existing_readme_md_and_html",
     True, True, [README_MD_ORIGINAL_NAME], []),
    ("tests/data/readme_to_markdown/has_no_readme", False, False, [],
     [README_MD_NAME, README_MD_ORIGINAL_NAME])
]


@pytest.fixture(scope='function')
def app_dir(request):
    def copy_test_dir():
        shutil.copytree(app_dir, app_dir_copy)

    def remove_test_dir_copy():
        shutil.rmtree(app_dir_copy, ignore_errors=True)

    app_dir = Path(request.param)
    app_dir_copy = Path(str(app_dir) + '_copy')

    copy_test_dir()
    request.addfinalizer(remove_test_dir_copy)

    return app_dir_copy


@pytest.mark.parametrize(("app_dir, check_output, expected_result, "
                          "expected_new_files, unexpected_new_files"),
                         TEST_DATA, indirect=["app_dir"])
def test_readme_to_markdown(app_dir, check_output, expected_result,
                            expected_new_files, unexpected_new_files):
    output_readme = os.path.join(app_dir, 'readme.md')
    expected_readme = os.path.join(app_dir, 'expected_readme.md')

    result, backup = readme_html_to_markdown(app_dir, None, None, False, False)
    if not expected_result:
        assert result is None

    if backup:
         assert os.path.isfile(backup)

    if check_output:
        with open(output_readme) as actual_f, open(expected_readme) as expected_f:
            actual_content = actual_f.read()
            assert actual_content == expected_f.read()

    for expected_new_file in expected_new_files:
        expected_new_file = os.path.join(app_dir, expected_new_file)
        assert os.path.isfile(expected_new_file)

    for unexpected_new_file in unexpected_new_files:
        unexpected_new_file = os.path.join(app_dir, unexpected_new_file)
        assert not os.path.isfile(unexpected_new_file)
