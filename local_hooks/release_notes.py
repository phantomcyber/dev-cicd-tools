from pathlib import Path
import re

UNRELEASED_MD_HEADER = "**Unreleased**"
RELEASE_NOTE_PATTERN = re.compile(r"^\* (?P<note>\S.*)$")
NESTED_LIST_MARKER_PATTERN = re.compile(r"^(?:[*+-]|\d+[.)])(?:\s|$)")


def check_release_notes(app_directory: str):
    release_notes_path = Path(app_directory) / "release_notes/unreleased.md"
    if not release_notes_path.exists():
        print(
            "Release notes file does not exist. Creating it now. This hook will still fail because it needs to be populated."
        )
        release_notes_path.write_text(UNRELEASED_MD_HEADER + "\n")
        raise ValueError("Release notes file is empty. Please populate it with release notes.")

    release_notes = release_notes_path.read_text().splitlines()
    if not release_notes:
        release_notes_path.write_text(UNRELEASED_MD_HEADER + "\n")
        raise ValueError("Release notes file is empty. Please populate it with release notes.")

    if release_notes[0] != UNRELEASED_MD_HEADER:
        raise ValueError(f"Release notes must start with '{UNRELEASED_MD_HEADER}'.")

    note_lines = list(enumerate(release_notes[1:], start=2))
    if note_lines and note_lines[0][1] == "":
        note_lines = note_lines[1:]

    if not note_lines:
        raise ValueError("Release notes file is empty. Please populate it with release notes.")

    for line_number, note in note_lines:
        match = RELEASE_NOTE_PATTERN.match(note)
        if not match:
            raise ValueError(
                f"Incorrectly formatted release note on line {line_number}: {note!r}. "
                "Expected a non-empty top-level '* ' list entry."
            )

        if NESTED_LIST_MARKER_PATTERN.match(match.group("note")):
            raise ValueError(
                f"Incorrectly formatted release note on line {line_number}: {note!r}. "
                "Nested or repeated list markers are not allowed."
            )


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("directory")

    args = parser.parse_args()
    exit(check_release_notes(args.directory))


if __name__ == "__main__":
    main()
