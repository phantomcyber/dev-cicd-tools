import datetime
import itertools
import logging
import os
import shutil

import pytest

from pathlib import Path

from build_docs import README_OUTPUT_NAME, main as build_docs_main, BuildDocsArgs

logging.getLogger().setLevel(logging.INFO)

START_RELEASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(scope="function")
def app_dir(request: pytest.FixtureRequest) -> Path:
    app_dir = Path(request.param)  # type: ignore
    app_dir_copy = Path(f"{app_dir}_copy")

    shutil.copytree(app_dir, app_dir_copy)

    def remove_test_dir_copy():
        shutil.rmtree(app_dir_copy, ignore_errors=True)

    request.addfinalizer(remove_test_dir_copy)

    return app_dir_copy


@pytest.mark.parametrize(
    ("app_dir, expected_new_files"),
    [
        ("tests/data/build_docs/has_existing_readme", []),
        ("tests/data/build_docs/has_no_readme", [README_OUTPUT_NAME]),
    ],
    indirect=["app_dir"],
)
def test_build_docs(capsys, app_dir: Path, expected_new_files: list[str]):
    output_readme = app_dir / "README.md"
    expected_readme = app_dir / "expected_readme.md"

    try:
        build_docs_main(BuildDocsArgs(connector_path=app_dir))
    except Exception as e:
        pytest.fail(str(e))

    year = datetime.datetime.now().year
    with output_readme.open() as actual, expected_readme.open() as expected:
        for num, (actual_line, expected_line) in enumerate(
            itertools.zip_longest(actual, expected), 1
        ):
            # Catch the auto-generated copyright year
            expected_line = expected_line.replace("{{year}}", str(year))

            assert actual_line == expected_line, (
                f"Line {num} differed from {expected_readme}:\n{actual_line=}\n{expected_line=}\n"
            )

    for expected_new_file in expected_new_files:
        expected_new_file = Path(app_dir, expected_new_file)
        assert expected_new_file.is_file()
