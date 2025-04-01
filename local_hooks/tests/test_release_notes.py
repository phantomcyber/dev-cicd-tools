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
    ["tests/data/release_notes/release_notes_passing"],
    indirect=["app_dir"],
)
def test_release_notes_passing(app_dir: Path):
    result = subprocess.run(
        [os.path.join(PRE_COMMIT_DIR, "release_notes.sh")],
        cwd=app_dir,
        capture_output=True,
    )
    print(result.stderr.decode())
    assert result.returncode == 0


@pytest.mark.parametrize(
    "app_dir",
    ["tests/data/release_notes/release_notes_failing/actual"],
    indirect=["app_dir"],
)
def test_release_notes_failing(app_dir: Path):
    expected_dir = Path("tests/data/release_notes/release_notes_failing/expected")
    expected_file = "release_notes/unreleased.md"

    result = subprocess.run(
        [os.path.join(PRE_COMMIT_DIR, "release_notes.sh")],
        cwd=app_dir,
        capture_output=True,
    )
    assert result.returncode == 0

    actual_path = app_dir / expected_file
    expected_path = expected_dir / expected_file

    assert actual_path.exists(), f"Missing expected file {expected_file}"
    print(actual_path.read_text())
    assert actual_path.read_text() == expected_path.read_text(), (
        f"Release note file {expected_file} did not match expectations!"
    )
