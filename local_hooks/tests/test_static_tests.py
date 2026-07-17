import logging
import os
import shutil
import subprocess
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from pathlib import Path

from local_hooks.app_tests.json_tests import JSONTests

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
@patch("local_hooks.app_tests.utils.app_parser.load_sdk_apps_environment")
@patch("local_hooks.app_tests.utils.app_parser.generate_sdk_app_manifest")
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


def test_pip313_dependencies_allows_empty_generated_wheel_set(tmp_path: Path):
    """SOAR-provided requirements do not need redundant bundled wheels."""
    (tmp_path / "requirements.txt").write_text("beautifulsoup4==4.12.2\n")
    suite = JSONTests.__new__(JSONTests)
    suite._app_code_dir = tmp_path
    suite._parser = SimpleNamespace(uv_lock_filepath=None)
    suite._app_json = {"pip313_dependencies": {"wheel": []}}

    result = suite.check_pip313_dependencies()

    assert result["success"] is True


def test_pip313_dependencies_still_requires_generated_key(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("beautifulsoup4==4.12.2\n")
    suite = JSONTests.__new__(JSONTests)
    suite._app_code_dir = tmp_path
    suite._parser = SimpleNamespace(uv_lock_filepath=None)
    suite._app_json = {}

    result = suite.check_pip313_dependencies()

    assert result["success"] is False
    assert result["message"] == (
        "App json must contain 'pip313_dependencies' key when requirements.txt exists"
    )


def test_connector_template_skips_published_identity_registry_checks():
    suite = JSONTests.__new__(JSONTests)
    suite._app_json = {
        "appid": "ffffffff-ffff-4fff-afff-ffffffffffff",
        "name": "Example App Name",
        "package_name": "phantom_template",
    }

    name_result = suite.check_valid_app_name_and_guid()
    package_result = suite.check_app_package_name()

    assert name_result["success"] is True
    assert name_result["message"] == "TEST SKIPPED - connector template placeholder detected"
    assert package_result["success"] is True
    assert package_result["message"] == name_result["message"]
