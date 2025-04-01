# Copyright (c) 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import shutil
import subprocess

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
    "app_dir",
    ["tests/data/static_tests/app_dir"],
    indirect=["app_dir"],
)
def test_static_tests(app_dir: Path):
    expected_dir = Path("tests/data/static_tests/expected")
    expected_files = ["statictests.json", "__init__.py"]

    result = subprocess.run(
        [os.path.join(PRE_COMMIT_DIR, "static_tests.sh")],
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
