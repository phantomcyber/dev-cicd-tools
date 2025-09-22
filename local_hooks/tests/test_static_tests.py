import logging
import os
import shutil
import subprocess
import json
from unittest.mock import patch

import pytest
from pathlib import Path

PRE_COMMIT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

logging.getLogger().setLevel(logging.INFO)


def copy_app_dir(request: pytest.FixtureRequest) -> Path:
    app_dir = Path(request.param)  # type: ignore
    app_dir_copy = Path(f"{app_dir}_copy")

    shutil.copytree(app_dir, app_dir_copy)

    def remove_test_dir_copy():
        shutil.rmtree(app_dir_copy, ignore_errors=True)

    request.addfinalizer(remove_test_dir_copy)

    return app_dir_copy


@pytest.fixture(scope="function")
def app_dir(request: pytest.FixtureRequest) -> Path:
    return copy_app_dir(request)


@pytest.fixture(scope="function")
def sdk_app_dir(request: pytest.FixtureRequest) -> Path:
    return copy_app_dir(request)


@pytest.mark.parametrize(
    "app_dir",
    ["tests/data/static_tests/app_dir"],
    indirect=["app_dir"],
)
def test_static_tests(app_dir: Path):
    expected_dir = Path("tests/data/static_tests/expected")
    expected_files = ["statictests.json", "__init__.py"]

    result = subprocess.run(
        ["static-tests", "."],
        cwd=app_dir,
        capture_output=True,
    )
    print(result.stderr.decode())
    assert result.returncode == 10

    for filename in expected_files:
        actual_path = app_dir / filename
        expected_path = expected_dir / filename

        assert actual_path.exists(), f"Missing expected file {filename}"
        assert actual_path.read_text() == expected_path.read_text()


@pytest.mark.parametrize(
    "sdk_app_dir",
    ["tests/data/static_tests/sdk_app_dir"],
    indirect=["sdk_app_dir"],
)
@patch("local_hooks.helpers.load_sdk_apps_enviornment")
@patch("local_hooks.helpers.generate_sdk_app_manifest")
def test_static_tests_sdkfied_app(mock_generate_manifest, mock_load_env, sdk_app_dir: Path):
    sdk_manifest_path = Path("tests/data/static_tests/sdk_app_dir/sdk_app_manifest.json")
    with open(sdk_manifest_path) as f:
        sdk_manifest_data = json.load(f)

    # Mock the helper functions
    mock_load_env.return_value = None
    mock_generate_manifest.return_value = sdk_manifest_data

    # Import and run static tests directly instead of subprocess
    from local_hooks.static_tests import main
    import sys

    # Save original args and cwd
    original_argv = sys.argv
    original_cwd = os.getcwd()

    try:
        sys.argv = ["static-tests", "."]
        os.chdir(sdk_app_dir)
        exit_code = main()

    finally:
        sys.argv = original_argv
        os.chdir(original_cwd)

    assert exit_code == 4
