import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from uuid import uuid4

from local_hooks.package_app_dependencies import AppJsonWheelEntry, _existing_wheel_constraints

PRE_COMMIT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def test_package_wrapper_does_not_install_os_packages():
    wrapper = Path(PRE_COMMIT_DIR, "package_app_dependencies.sh").read_text()

    assert "yum install" not in wrapper
    assert "dnf install" not in wrapper


def test_committed_wheels_constrain_normal_dependency_packaging():
    constraints = _existing_wheel_constraints(
        [
            AppJsonWheelEntry("PyNaCl", "wheels/py36/PyNaCl-1.5.0-cp36-abi3-manylinux.whl"),
            AppJsonWheelEntry("pycparser", "wheels/py3/pycparser-2.22-py3-none-any.whl"),
        ]
    )

    assert constraints == ["PyNaCl==1.5.0", "pycparser==2.22"]


@pytest.fixture(
    scope="function",
    params=[
        "tests/data/py3-app",
        "tests/data/pure-python-py3-app",
    ],
)
def app_dir(request):
    def backup_files():
        if os.path.exists(wheels_dir):
            shutil.copytree(wheels_dir, wheels_dir_copy)
        shutil.copy(app_json, app_json_copy)

    def restore_files():
        shutil.rmtree(wheels_dir, ignore_errors=True)
        if os.path.exists(wheels_dir_copy) and not os.path.exists(wheels_dir):
            os.rename(wheels_dir_copy, wheels_dir)

        os.remove(app_json)
        os.rename(app_json_copy, app_json)

    app_dir = request.param
    backup_uid = uuid4().hex

    wheels_dir = os.path.join(app_dir, "wheels")
    wheels_dir_copy = os.path.join(app_dir, f"wheels-copy-{backup_uid}")

    app_json = os.path.join(app_dir, "app.json")
    app_json_copy = os.path.join(app_dir, f"app_json_copy_{backup_uid}.txt")

    backup_files()
    request.addfinalizer(restore_files)

    return app_dir


@pytest.mark.parametrize(
    "flags", [[], ["-d", "./Dockerfile.wheels"], ["-i", "quay.io/pypa/manylinux2014_x86_64"]]
)
def test_app_with_pip_dependencies(flags, app_dir):
    app_json = os.path.join(app_dir, "app.json")
    expected_app_json = os.path.join(app_dir, "expected_app_json.out")
    expected_app_json_2 = os.path.join(app_dir, "expected_app_json_2.out")

    result = subprocess.run(
        [os.path.join(PRE_COMMIT_DIR, "package_app_dependencies.sh"), *flags],
        cwd=app_dir,
        capture_output=True,
    )
    print(result.stderr.decode())
    assert result.returncode == 0

    if os.path.exists(expected_app_json_2):
        with (
            open(app_json) as actual_f,
            open(expected_app_json) as expected_f,
            open(expected_app_json_2) as expected_f_2,
        ):
            actual = json.load(actual_f)
            expected = json.load(expected_f)
            expected_2 = json.load(expected_f_2)
            print(f"Actual: {actual}")
            print(f"Expected: {expected}")
            print(f"Expected 2: {expected_2}")

        assert actual == expected or actual == expected_2
    else:
        with open(app_json) as actual_f, open(expected_app_json) as expected_f:
            actual = json.load(actual_f)
            expected = json.load(expected_f)

        assert actual == expected

    # Check that all wheel files exist for pip39_dependencies
    if "pip39_dependencies" in actual:
        for whl in actual["pip39_dependencies"]["wheel"]:
            assert os.path.exists(os.path.join(app_dir, whl["input_file"]))

    # Check that all wheel files exist for pip313_dependencies
    if "pip313_dependencies" in actual:
        for whl in actual["pip313_dependencies"]["wheel"]:
            assert os.path.exists(os.path.join(app_dir, whl["input_file"]))
