import datetime
import itertools
import logging
import os
import shutil
import subprocess
import textwrap

import pytest

from pathlib import Path

PRE_COMMIT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

logging.getLogger().setLevel(logging.INFO)


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
        ("tests/data/build_docs/has_no_readme", ["README.md"]),
    ],
    indirect=["app_dir"],
)
def test_build_docs(app_dir: Path, expected_new_files: list[str]):
    output_readme = app_dir / "README.md"
    expected_readme = app_dir / "expected_readme.md"

    result = subprocess.run(
        ["python", os.path.join(PRE_COMMIT_DIR, "build_docs.py")],
        cwd=app_dir,
        capture_output=True,
    )
    print(result.stderr.decode())
    assert result.returncode == 0

    year = datetime.datetime.now().year
    with output_readme.open() as actual, expected_readme.open() as expected:
        for num, (actual_line, expected_line) in enumerate(
            itertools.zip_longest(actual, expected), 1
        ):
            # Catch the auto-generated copyright year
            expected_line = expected_line.replace("{{year}}", str(year))

            assert actual_line == expected_line, textwrap.dedent(
                f"""
                Line {num} differed from {expected_readme}:
                  {actual_line=}
                {expected_line=}

                """
            )

    for expected_new_file in expected_new_files:
        expected_new_file = Path(app_dir, expected_new_file)
        assert expected_new_file.is_file()

    # README updates should be idempotent
    result = subprocess.run(
        [os.path.join(PRE_COMMIT_DIR, "build_docs.sh")],
        cwd=app_dir,
        capture_output=True,
    )
    assert result.returncode == 0
