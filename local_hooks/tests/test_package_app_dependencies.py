import json
import os
import shutil
import subprocess

import pytest
from uuid import uuid4

PRE_COMMIT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


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

    for whl in actual["pip39_dependencies"]["wheel"]:
        assert os.path.exists(os.path.join(app_dir, whl["input_file"]))
