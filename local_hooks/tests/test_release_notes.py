from pathlib import Path
import subprocess

import pytest

from local_hooks.release_notes import UNRELEASED_MD_HEADER, check_release_notes


def write_release_notes(app_dir: Path, content: str) -> None:
    release_notes_dir = app_dir / "release_notes"
    release_notes_dir.mkdir()
    (release_notes_dir / "unreleased.md").write_text(content)


@pytest.mark.parametrize(
    "content",
    [
        "**Unreleased**\n* Updated dependencies.\n",
        "**Unreleased**\n\n* Updated dependencies.\n",
        "**Unreleased**\n\n* Updated `urllib3`.\n* Fixed request handling.\n",
    ],
)
def test_release_notes_accepts_top_level_bullets(tmp_path: Path, content: str):
    write_release_notes(tmp_path, content)

    check_release_notes(str(tmp_path))


def test_release_notes_command_accepts_canonical_content(tmp_path: Path):
    write_release_notes(tmp_path, "**Unreleased**\n\n* Updated dependencies.\n")

    result = subprocess.run(["release-notes", "."], cwd=tmp_path, capture_output=True)

    assert result.returncode == 0


@pytest.mark.parametrize(
    ("content", "error"),
    [
        ("**Unreleased**\n\n* Parent note.\n    * Nested note.\n", "top-level"),
        ("**Unreleased**\n\n* - Updated dependency.\n", "repeated list markers"),
        (
            "**Unreleased**\n\n* Updated first dependency.\n\n* Updated second dependency.\n",
            "top-level",
        ),
        ("**Unreleased**\n\nUpdated dependencies.\n", "top-level"),
        ("**Unreleased**\n\n* \n", "top-level"),
    ],
)
def test_release_notes_rejects_noncanonical_content(tmp_path: Path, content: str, error: str):
    write_release_notes(tmp_path, content)

    with pytest.raises(ValueError, match=error):
        check_release_notes(str(tmp_path))


def test_missing_release_notes_file_is_created_and_rejected(tmp_path: Path):
    release_notes_dir = tmp_path / "release_notes"
    release_notes_dir.mkdir()

    with pytest.raises(ValueError, match="empty"):
        check_release_notes(str(tmp_path))

    assert (release_notes_dir / "unreleased.md").read_text() == f"{UNRELEASED_MD_HEADER}\n"
