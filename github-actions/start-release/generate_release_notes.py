import datetime
import logging
import os
import re

RELEASE_NOTES_DIR = 'release_notes'
UNRELEASED_MD = '{}/unreleased.md'.format(RELEASE_NOTES_DIR)
RELEASE_NOTES_HTML = '{}/release_notes.html'.format(RELEASE_NOTES_DIR)
UNRELEASED_MD_HEADER = '**Unreleased**'
RELEASE_NOTES_MD = RELEASE_NOTES_DIR + '/{}.md'
RELEASE_NOTES_TOP_HEADER = '**{} Release Notes - Published by {} {}**\n\n'
RELEASE_NOTES_VERSION_HEADER = '**Version {} - Released {}**\n'
RELEASE_NOTES_DATE_FORMAT = '%B %d, %Y'
RELEASE_NOTE_PATTERN = re.compile(r'^\s*\* (?P<note>.+)$')

# The minimum number of white spaces a nested list entry needs to be
# indented from its parent for it be rendered correctly on GitHub
MD_NESTED_LIST_MIN_INDENT = 2

# The maximum number of white spaces a nested list entry can be
# indented from its parent for it to be rendered correctly on GitHub
MD_NESTED_LIST_MAX_INDENT = 5


FIRST_VERSION = '1.0.0'


def append_release_notes_md(app_dir, release_version, unreleased_notes):
    if unreleased_notes[0] != UNRELEASED_MD_HEADER:
        raise ValueError('Expected the first line of {} to be the header {}'
                         .format(UNRELEASED_MD, UNRELEASED_MD_HEADER))

    existing_release_notes = os.path.join(app_dir, f'release_notes/{release_version}.md')
    if os.path.isfile(existing_release_notes):
        with open(existing_release_notes) as f:
            release_notes = f.read().split('\n')
    else:
        release_notes = []

    parent_depths = []
    for note in unreleased_notes[1:]:
        if not note or not note.strip():
            continue
        match = RELEASE_NOTE_PATTERN.match(note)
        if not match:
            raise ValueError('Detected incorrectly formatted release note: \'{}\''
                             .format(note))
        note = match.group()

        cur_depth, parent_depth = note.index('*'), parent_depths[-1] if parent_depths else 0
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
            raise ValueError(f'Nested list entry {note} is too far indented from its parent')
        # Current note starts a new nested list - record the depth of the new list
        elif MD_NESTED_LIST_MIN_INDENT <= depth_diff:
            parent_depths.append(cur_depth)
        # Current note is on the same level as the previous
        else:
            pass

        release_notes.append(note)

    if not release_notes:
        return None

    return '\n'.join(release_notes)


def _find_notes_for_current_release(release_notes_html, current_release):
    current_release_regex = re.compile(rf'^<b>Version {current_release} - Released.+</b>$')
    for idx, line in enumerate(release_notes_html or []):
        current_releaser_header = current_release_regex.match(line)
        if current_releaser_header:
            next_idx = idx + 1
            if release_notes_html[next_idx] != '<ul>':
                raise ValueError(f'Expected line {idx + 1} to be the start of a list <ul> but got {release_notes_html[next_idx]}')

            while True:
                next_idx += 1
                if next_idx >= len(release_notes_html):
                    raise ValueError(f'Could not find closing </ul> in {release_notes_html}')

                element = release_notes_html[next_idx]
                if element == '</ul>':
                    return next_idx
    return -1


def update_release_notes_html(old_release_notes_html, release_version, unreleased_notes, app_json):
    """
    Updates the app's HTML release notes with the latest notes from unreleased.md
    first converting from Markdown to HTML.

    HTML release notes are cumulative and sorted by revision in descending order, the new
    release notes are added at the top of the file after the first header.

    TODO: This code can be removed once Phantom Portal is retired
          https://jira.splunk.com/browse/PAPP-21215
    """
    # Prepend a top level header with updated publish date, and a version header
    # for the new release notes
    publish_date = datetime.date.today().strftime(RELEASE_NOTES_DATE_FORMAT)
    new_notes_html = [
        '<b>{} Release Notes - Published by {} {}</b>'.format(
            app_json['name'], app_json['publisher'], publish_date),
        '<br><br>',
        '<b>Version {} - Released {}</b>'.format(release_version, publish_date),
        '<ul>'
    ]

    # Check if there's existing notes for the current release, we'll want to append the
    # new notes to the existing notes
    notes_for_current_release_end_idx = _find_notes_for_current_release(old_release_notes_html,
                                                                        release_version)
    if notes_for_current_release_end_idx > -1:
        # Skip past the existing headers since we've re-generated them with updated dates
        # Do not include the closing </ul> tag since we'll be appending new notes
        new_notes_html.extend(old_release_notes_html[len(new_notes_html):notes_for_current_release_end_idx])

    # Write the new release notes, converting bulleted lists in Markdown to HTML
    if unreleased_notes[0] != UNRELEASED_MD_HEADER:
        raise ValueError('Expected the first line of {} to be the header {}'
                         .format(UNRELEASED_MD, UNRELEASED_MD_HEADER))

    parent_depths = []
    for note_md in unreleased_notes[1:]:
        if not note_md.strip():
            continue

        note = RELEASE_NOTE_PATTERN.match(note_md).group('note')

        cur_note_depth = note_md.index('*')
        parent_depth = parent_depths[-1] if parent_depths else 0
        depth_diff = cur_note_depth - parent_depth

        # Check if we're starting a nested list, no need to check for over-indentation
        # since the markdown was already validated
        if depth_diff >= MD_NESTED_LIST_MIN_INDENT:
            parent_depths.append(cur_note_depth)
            new_notes_html.append('<ul>')
        # Check if we're ending a nested list
        elif depth_diff < 0:
            while True:
                parent_depths.pop()
                new_notes_html.append('</ul>')
                depth_diff = cur_note_depth - parent_depths[-1] if parent_depths else 0
                if depth_diff >= 0:
                    break

        new_notes_html.append('<li>{}</li>'.format(note))

    new_notes_html.append('</ul>')

    if notes_for_current_release_end_idx != -1:
        # We've included the existing notes for the current release into the new release notes,
        # append the remaining notes for past releases
        new_notes_html.extend(old_release_notes_html[notes_for_current_release_end_idx + 1:])
    elif old_release_notes_html:
        # Read the previous release notes to find the linebreak separating the
        # top header from the release notes, then copy the previous release notes
        # into the new release notes
        line_break_idx = -1
        while True:
            line_break_idx += 1
            if line_break_idx >= len(old_release_notes_html):
                raise ValueError('Could not find expected linebreak in HTML release notes')
            elif old_release_notes_html[line_break_idx] == '<br><br>':
                break

        new_notes_html.extend(old_release_notes_html[line_break_idx + 1:])

    return '\n'.join(new_notes_html)


def generate_release_notes(app_dir, release_version, app_json):
    # Generate release notes for the new app version from the entries
    # in unreleased.md, then truncate unreleased.md
    updates = {}
    with open(os.path.join(app_dir, UNRELEASED_MD)) as f:
        unreleased_notes_md = f.read().split('\n')

    if all(n == UNRELEASED_MD_HEADER or not n.strip() for n in unreleased_notes_md):
        logging.info('Did not detect any new notes to release!')
        return updates

    release_notes_md = append_release_notes_md(app_dir,
                                               release_version,
                                               unreleased_notes_md)

    logging.info('Generated release notes for version %s:', release_version)

    logging.info(release_notes_md)
    updates[RELEASE_NOTES_MD.format(release_version)] = release_notes_md

    try:
        with open(os.path.join(app_dir, RELEASE_NOTES_HTML)) as f:
            old_release_notes_html = f.read().split('\n')
    except FileNotFoundError:
        old_release_notes_html = None

    new_release_notes_html = update_release_notes_html(old_release_notes_html,
                                                       release_version,
                                                       unreleased_notes_md,
                                                       app_json)
    updates[RELEASE_NOTES_HTML] = new_release_notes_html

    unreleased_notes = UNRELEASED_MD_HEADER + '\n'
    updates[UNRELEASED_MD] = unreleased_notes

    return updates
