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
from pathlib import Path
import re

UNRELEASED_MD_HEADER = "**Unreleased**"
RELEASE_NOTE_PATTERN = re.compile(r"^\s*\* (?P<note>.+)$")
# The minimum number of white spaces a nested list entry needs to be
# indented from its parent for it be rendered correctly on GitHub
MD_NESTED_LIST_MIN_INDENT = 2

# The maximum number of white spaces a nested list entry can be
# indented from its parent for it to be rendered correctly on GitHub
MD_NESTED_LIST_MAX_INDENT = 5


def check_release_notes(app_directory: str):
    release_notes_path = Path(app_directory) / "release_notes/unreleased.md"
    if not release_notes_path.exists():
        print(
            "Release notes file does not exist. Creating it now. This hook will still fail because it needs to be populated."
        )
        release_notes_path.write_text(UNRELEASED_MD_HEADER + "\n")
        raise ValueError("Release notes file is empty. Please populate it with release notes.")

    release_notes = release_notes_path.read_text().rstrip().splitlines()
    if not release_notes:
        release_notes_path.write_text(UNRELEASED_MD_HEADER + "\n")
        raise ValueError("Release notes file is empty. Please populate it with release notes.")

    incorrect_format = False

    if release_notes[0] != UNRELEASED_MD_HEADER:
        # assuming that the first line is a note
        release_notes.insert(0, UNRELEASED_MD_HEADER)

    if len(release_notes) == 1:
        raise ValueError("Release notes file is empty. Please populate it with release notes.")

    parent_depths = []
    for i in range(1, len(release_notes)):
        note = release_notes[i]
        if not note or not note.strip():
            continue

        match = RELEASE_NOTE_PATTERN.match(note)
        if not match:
            leading_whitespace = re.match(r"^\s*", note).group()
            new_note = f"{leading_whitespace}* {note.strip()}"
            if not (
                match := RELEASE_NOTE_PATTERN.match(new_note)
            ):  # check if the note is still incorrect
                # fix any successfully caught errors found before
                if incorrect_format:
                    release_notes_path.write_text("\n".join(release_notes) + "\n")
                raise ValueError(
                    f"Detected incorrectly formatted release note: '{note}'. Tried fixing but failed."
                )
            else:
                incorrect_format = True
                release_notes[i] = new_note
                print(f"Fixed release note formatting for {note}.")

        note = match.group()
        cur_depth, parent_depth = note.index("*"), parent_depths[-1] if parent_depths else 0
        depth_diff = cur_depth - parent_depth
        # Previous nested list ended and we're moving back up one or more levels
        if depth_diff < 0:
            while True:
                parent_depths.pop()
                depth_diff = cur_depth - parent_depths[-1] if parent_depths else 0
                if depth_diff >= 0:
                    break
        # Current note is too far indented from its parent
        elif depth_diff > MD_NESTED_LIST_MAX_INDENT:
            incorrect_format = True
            new_depth = parent_depth + MD_NESTED_LIST_MAX_INDENT - 1
            note = " " * new_depth + note.lstrip()
            release_notes[i] = note
            print(f"Fixed indentation for {note}.")
        # Current note starts a new nested list - record the depth of the new list
        elif MD_NESTED_LIST_MIN_INDENT <= depth_diff:
            parent_depths.append(cur_depth)
        # Current note is on the same level as the previous
        else:
            pass

    # fix errors if any were found
    if incorrect_format:
        release_notes_path.write_text("\n".join(release_notes) + "\n")
        print("Release notes file has been updated with corrected formatting.")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("directory")

    args = parser.parse_args()
    exit(check_release_notes(args.directory))


if __name__ == "__main__":
    main()
