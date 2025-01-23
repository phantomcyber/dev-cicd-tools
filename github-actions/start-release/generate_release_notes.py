import logging
import os
import re

RELEASE_NOTES_DIR = "release_notes"
UNRELEASED_MD = f"{RELEASE_NOTES_DIR}/unreleased.md"
UNRELEASED_MD_HEADER = "**Unreleased**"
RELEASE_NOTES_MD = RELEASE_NOTES_DIR + "/{}.md"
RELEASE_NOTES_TOP_HEADER = "**{} Release Notes - Published by {} {}**\n\n"
RELEASE_NOTES_VERSION_HEADER = "**Version {} - Released {}**\n"
RELEASE_NOTES_DATE_FORMAT = "%B %d, %Y"
RELEASE_NOTE_PATTERN = re.compile(r"^\s*\* (?P<note>.+)$")

# The minimum number of white spaces a nested list entry needs to be
# indented from its parent for it be rendered correctly on GitHub
MD_NESTED_LIST_MIN_INDENT = 2

# The maximum number of white spaces a nested list entry can be
# indented from its parent for it to be rendered correctly on GitHub
MD_NESTED_LIST_MAX_INDENT = 5


FIRST_VERSION = "1.0.0"


def append_release_notes_md(app_dir, release_version, unreleased_notes):
    if unreleased_notes[0] != UNRELEASED_MD_HEADER:
        raise ValueError(
            f"Expected the first line of {UNRELEASED_MD} to be the header {UNRELEASED_MD_HEADER}"
        )

    existing_release_notes = os.path.join(app_dir, f"release_notes/{release_version}.md")
    if os.path.isfile(existing_release_notes):
        with open(existing_release_notes) as f:
            release_notes = f.read().split("\n")
    else:
        release_notes = []

    parent_depths = []
    for note in unreleased_notes[1:]:
        if not note or not note.strip():
            continue
        match = RELEASE_NOTE_PATTERN.match(note)
        if not match:
            raise ValueError(f"Detected incorrectly formatted release note: '{note}'")
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
            raise ValueError(f"Nested list entry {note} is too far indented from its parent")
        # Current note starts a new nested list - record the depth of the new list
        elif MD_NESTED_LIST_MIN_INDENT <= depth_diff:
            parent_depths.append(cur_depth)
        # Current note is on the same level as the previous
        else:
            pass

        release_notes.append(note)

    if not release_notes:
        return None

    return "\n".join(release_notes)


def generate_release_notes(app_dir, release_version, app_json):
    # Generate release notes for the new app version from the entries
    # in unreleased.md, then truncate unreleased.md
    updates = {}
    with open(os.path.join(app_dir, UNRELEASED_MD)) as f:
        unreleased_notes_md = f.read().split("\n")

    if all(n == UNRELEASED_MD_HEADER or not n.strip() for n in unreleased_notes_md):
        logging.info("Did not detect any new notes to release!")
        return updates

    release_notes_md = append_release_notes_md(app_dir, release_version, unreleased_notes_md)

    logging.info("Generated release notes for version %s:", release_version)

    logging.info(release_notes_md)
    updates[RELEASE_NOTES_MD.format(release_version)] = release_notes_md

    unreleased_notes = UNRELEASED_MD_HEADER + "\n"
    updates[UNRELEASED_MD] = unreleased_notes

    return updates
