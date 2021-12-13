import logging
import os
import shutil
import subprocess

import pytest

from pathlib import Path

from build_docs import build_docs_from_html, README_OUTPUT_NAME
from readme_to_markdown import README_MD_ORIGINAL_NAME

logging.getLogger().setLevel(logging.INFO)

START_RELEASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

FROM_MD_TEST_DATA = [
    ("tests/data/build_docs/has_existing_readme", 0, True, []),
    ("tests/data/build_docs/has_no_readme", 0, True, [README_OUTPUT_NAME])
]

FROM_HTML_TEST_DATA = [
    ("tests/data/build_docs/has_existing_readme_html_and_md", True, [README_MD_ORIGINAL_NAME], [], None),
    ("tests/data/build_docs/has_existing_readme_html_and_autogen_md", True, [], [README_MD_ORIGINAL_NAME], None),
    ("tests/data/build_docs/has_no_readme", True, [README_OUTPUT_NAME], [], None),
    ("tests/data/build_docs/has_no_readme_set_app_version", True, [README_OUTPUT_NAME], [], "3.0.0")
]

@pytest.fixture(scope='function')
def app_dir(request):
    def copy_test_dir():
        shutil.copytree(app_dir, app_dir_copy)

    def remove_test_dir_copy():
        shutil.rmtree(app_dir_copy, ignore_errors=True)

    app_dir = request.param
    app_dir_copy = app_dir + '_copy'

    copy_test_dir()
    request.addfinalizer(remove_test_dir_copy)

    return app_dir_copy


@pytest.mark.parametrize(("app_dir, expected_exit_code, check_output, "
                          "expected_new_files"), FROM_MD_TEST_DATA,
                          indirect=["app_dir"])
def test_build_docs(app_dir, expected_exit_code,
                    check_output, expected_new_files):
    output_readme = os.path.join(app_dir, 'README.md')
    expected_readme = os.path.join(app_dir, 'expected_readme.md')

    result = subprocess.run([os.path.join(START_RELEASE_DIR, 'build_docs')],
                            cwd=app_dir,
                            capture_output=True)
    print(result.stderr.decode())
    assert result.returncode == expected_exit_code

    if check_output:
        with open(output_readme) as actual_f, open(expected_readme) as expected_f:
            actual_content = actual_f.read()
            assert actual_content == expected_f.read()

    for expected_new_file in expected_new_files:
        expected_new_file = os.path.join(app_dir, expected_new_file)
        assert os.path.isfile(expected_new_file)


@pytest.mark.parametrize(("app_dir, check_output, expected_new_files, "
                          "unexpected_new_files, app_version"), FROM_HTML_TEST_DATA,
                          indirect=["app_dir"])
def test_build_docs_from_html(app_dir, check_output, expected_new_files,
                              unexpected_new_files, app_version):
    output_readme = os.path.join(app_dir, 'README.md')
    expected_readme = os.path.join(app_dir, 'expected_readme.md')

    build_docs_from_html(Path(app_dir), app_version)

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
