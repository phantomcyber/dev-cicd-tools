"""
Converts readme.html documents to README.md

This script has dependencies on some binary libraries.

To install tidy:
- ubuntu: run `apt-get update && apt-get install -y tidy`
- macOS: run `brew install tidy-html5`

To install pandoc:
- Get pandoc 2.16.2 from https://github.com/jgm/pandoc/releases
- ubuntu:
    wget https://github.com/jgm/pandoc/releases...pandoc-2.16.2-1-amd64.deb
    sudo dpkg -i pandoc-2.16.2-1-amd64.deb
- macOS:
    brew install pandoc or
    https://pandoc.org/installing.html#macos


WARNING: This script uses features only available in Python 3.8+.
         Make sure you are running Python 3.8 or later.
"""

import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import pypandoc
from bs4 import BeautifulSoup, Comment
from gh_md_to_html import core_converter
from tidylib import tidy_document

README_HTML_NAME = "readme.html"
README_MD_NAME = "README.md"
README_MD_ORIGINAL_NAME = "notes.md"
ORIGINAL_ATTRIBUTE_NAME = "data-original-6a350139-f584-4810-a736-19b01021e0c9"
ORIGINAL_ATTRIBUTE_VALUE = "1"
INVISIBLE_TAGS = ["style", "script", "head", "title", "meta", "[document]"]
HEADER_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]


def validate_html(html_content):
    document, errors = tidy_document(html_content)
    return document, errors


def html_to_md(html_content):
    return pypandoc.convert_text(html_content, "gfm",
                                 format="html", extra_args=["--columns=100"])


def md_to_html(md_content, use_pandoc=True):
    if use_pandoc:
        return pypandoc.convert_text(md_content, "html", format="gfm")
    else:
        return core_converter.markdown(md_content)


def parse_html(html_content):
    return BeautifulSoup(html_content, "html.parser")


def get_html_comments(parsed_html_content):
    comments = parsed_html_content.find_all(
        string=lambda text: isinstance(text, Comment))
    all_lines = [line for comment in comments for line in comment.split("\n")]
    return all_lines


def generate_md_comments(comments):
    updated_comments = [str(c).replace(README_HTML_NAME, README_MD_NAME)
                        for c in comments]
    updated_comments = [c.replace('"', "'") for c in updated_comments]
    return "\n".join([f"[comment]: # \"{uc}\""
                     for uc in updated_comments]) + "\n"


def tag_visible(element):
    if element.parent.name in INVISIBLE_TAGS:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_visible_text_from_html(parsed_html_content):
    texts = parsed_html_content.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)


def calculate_html_stats(parsed_html_content):
    rendered_text = get_visible_text_from_html(parsed_html_content)
    words = rendered_text.split()
    return len(rendered_text), len(words), words


def save_text(base_path, suffix, text_content):
    output_path = Path(base_path.with_suffix(suffix))
    with open(output_path, "w") as output_file:
        output_file.write(text_content)


def save_word_lists(base_path, original_words, converted_words):
    save_text(base_path, ".original_words", "\n".join(original_words))
    save_text(base_path, ".converted_words", "\n".join(converted_words))


def get_app_json(app_json_dir):
    app_json = [f for f in os.listdir(app_json_dir) if f.endswith(".json")
                and "postman_collection" not in f][0]
    with open(Path(app_json_dir, app_json), "r") as json_file:
        return json.load(json_file)


def add_original_attribute(parsed_html_content, element_name):
    all_matched_elements = parsed_html_content.find_all(element_name)
    for matched_element in all_matched_elements:
        matched_element[ORIGINAL_ATTRIBUTE_NAME] = ORIGINAL_ATTRIBUTE_VALUE


def remove_original_attribute(parsed_html_content, element_name):
    all_matched_elements = parsed_html_content.find_all(element_name)
    for matched_element in all_matched_elements:
        del matched_element[ORIGINAL_ATTRIBUTE_NAME]


def fix_misplaced_list_content_wrappers(parsed_html_content):
    """
    Some html documents contain invalid list content like
       <ol>
         <h3><li>Hello</li></h3>
    In cases like this, instead of wrapping the <li> with <h3> we should move
    the <h3> into the <li> and wrap the contents
    """

    list_names = ["ul", "ol"]
    all_list_elements = parsed_html_content.find_all(list_names)
    for list_element in all_list_elements:
        for item in list_element.contents:
            if (item.name not in list_names and item.name != "li"
                    and hasattr(item, 'contents') and item.contents):

                first_contained_item = item.contents[0]
                if first_contained_item.name == "li":
                    unwrapped = item.unwrap()
                    while first_contained_item.contents:
                        unwrapped.append(first_contained_item.contents[0])
                    first_contained_item.append(unwrapped)


def fix_incomplete_colgroups(parsed_html_content):
    """
    In some cases, there is a colgroup with fewer columns than the actual
    table has. After validation/conversion, this leads to entire columns
    missing in markdown.
      <table>
        <colgroup>
          <col style="width: 50px">
          <col style="width: 200px">
        </colgroup>
        <tr>
          <th>Setting</th>
          <th>Description</th>
          <th>Notes</th>
        </tr>
    We should detect when this happens and ensure the colgroup has the correct
    number of columns

    We also see <col> tags without an enclosing <colgroup>. This is valid, but
    when it happens it's more difficult to apply the fix above.
    """

    all_tables = parsed_html_content.find_all("table")
    for table in all_tables:
        """
        markdown tables require headers. to avoid generating an empty header
        row, if the first row doesn't contain th elements, convert td to th
        """
        first_row = table.find("tr")
        th_list = first_row.find_all('th')
        if not th_list:
            td_list = first_row.find_all('td')
            for td in td_list:
                td.name = 'th'

        colgroups = table.find_all("colgroup")
        if len(colgroups) < 1:
            col_elements = table.find_all("col")
            if len(col_elements) < 1:
                continue

            colgroups = [parsed_html_content.new_tag("colgroup")]
            col_elements[0].insert_before(colgroups[0])
            for col in col_elements:
                colgroups[0].append(col)

        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) > 0:
                break

        colgroup_cols = colgroups[0].find_all("col")
        cols_to_add = len(cells) - len(colgroup_cols)
        for i in range(cols_to_add):
            # new_col = copy.copy(colgroup_cols[0])
            new_col = parsed_html_content.new_tag("col")
            colgroups[0].append(new_col)


def remove_double_bullets(parsed_html_content):
    """
    After running HTML tidy, it will turn:
    <ul>
      <li>a</li>
      <ul><li>b</li></ul>
    into
    <ul>
      <li>a</li>
      <li><ul><li>b</li></ul></li>
    Which is correct, but now we have an extra bullet. In markdown, it would
    look like this:
    -   a
    -   -   b
    If we detect cases where that extra bullet is generated, we can correct
    it by appending the <ul> to the previous <li> instead of creating a new
    <li> for it

    This also can occur for plain text like:
       <ul>
           <li>text</li>
               &nbsp;&nbsp;{<br>
               &nbsp;&nbsp;&nbsp;&nbsp;"asset": {<br>
    The text outside the <li> will get wrapped in an <li> which will lead to
    extra bullets. We'll deal with that in a similar way as above, except
    we'll collect all the out-of-place text and put it in a <p> before
    appending to the previous <li>
    """

    all_text_elements = parsed_html_content.find_all(text=True)
    all_list_elements = parsed_html_content.find_all(["ul", "ol"])
    for list_or_text_element in all_text_elements + all_list_elements:
        parent = list_or_text_element.parent
        parent_previous_siblings = list(parent.previous_siblings)

        if (parent and parent.name == "li" and ORIGINAL_ATTRIBUTE_NAME
                not in parent.attrs and len(parent_previous_siblings) > 1
                and str(parent_previous_siblings[0]) == "\n"
                and parent_previous_siblings[1].name == "li"):

            removed = parent.extract()
            if not list_or_text_element.name:
                p_tag = parsed_html_content.new_tag("p")
                p_tag.append(parsed_html_content.new_tag("br"))
                while removed.contents:
                    p_tag.append(removed.contents[0])
                parent_previous_siblings[1].append(p_tag)
                continue

            while removed.contents:
                parent_previous_siblings[1].append(removed.contents[0])

    # Find and remove any list items that only contain whitespace
    all_list_item_elements = parsed_html_content.find_all(["li"])
    for list_item_element in all_list_item_elements:
        text = list_item_element.get_text()
        text_with_no_whitespace = ''.join(text.split())
        if not text_with_no_whitespace:
            list_item_element.extract()


def find_closest_element(from_element, tag_names_to_find):
    prev = from_element.find_previous(tag_names_to_find)
    next = from_element.find_next(tag_names_to_find)

    start_location = from_element.sourceline + from_element.sourcepos
    if prev and next:
        prev_location = prev.sourceline + prev.sourcepos
        next_location = next.sourceline + next.sourcepos

        distance_to_prev = abs(start_location - prev_location)
        distance_to_next = abs(start_location - next_location)

        if (distance_to_prev <= distance_to_next):
            return prev

        return next
    elif prev:
        return prev
    elif next:
        return next
    else:
        return None


def generate_gh_fragment(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text)
    return re.sub(r"[\s]", "-", text)


def fix_relative_links(parsed_html_content, app_json_dir_path,
                       tag_name, attribute):
    """
    Cases for problematic relative links:
    - images
    - actual hyperlinks
    - different section within the readme

    For the latter: some html containing links to other sections of the same
    page don't convert properly to markdown. Example:

    Link to <a href="#actions-api-version"><u>this section</u></a>.
    <p id="actions-api-version">
      <h2>API Versions used in the actions</h2>
      Some text
    </p>

    gets converted to:

    Link to [<u>this section</u>][].

    ## API Versions used in the actions

    Some text

      [<u>this section</u>]: #actions-api-version

    Which doesn't contain a working link
    We'll attempt to correct this by replacing the fragment component of the
    link with one that github-flavored-markdown will be ok with, based on the
    text of the closest header.
    """

    all_linking_elements = parsed_html_content.find_all(tag_name)
    for linking_element in all_linking_elements:
        url = linking_element.get(attribute, "")
        parsed_url = urlparse(url)
        is_absolute = bool(parsed_url.netloc)
        if not is_absolute and url:
            url_path_name = Path(parsed_url.path).name

            # Anchor in a different section of same document (fragment URL)
            file_to_find = url_path_name
            fragment = parsed_url.fragment
            if fragment:
                # Find the fragment elsewhere in the document
                # <anything id="hello">
                linked_element = parsed_html_content.find(id=fragment)

                # Find closest heading to linked element & get heading text
                if linked_element:
                    if (linked_element.name.startswith("h")
                            and len(linked_element.name) == 2):

                        closest_heading = linked_element
                    else:
                        closest_heading = find_closest_element(linked_element,
                                                               HEADER_TAGS)

                    if closest_heading:
                        closest_heading = closest_heading.get_text(strip=True)
                        fragment = generate_gh_fragment(closest_heading)

            # Try to find what we're linking to in the local filesystem, so we
            # know how much of the path to include in the new relative link
            matches = list(app_json_dir_path.rglob(file_to_find))
            if matches and file_to_find:
                new_url = matches[0].relative_to(app_json_dir_path)
                if fragment:
                    new_url = f"{new_url}#{fragment}"
                linking_element[attribute] = new_url
            elif fragment:
                linking_element[attribute] = f"{file_to_find}#{fragment}"


def readme_html_to_markdown(connector_path, connector_name=None,
                            output_folder=None, overwrite=False,
                            debug_mode=False):

    readme_html = Path(connector_path, README_HTML_NAME)
    if not readme_html.is_file():
        return (None, None)

    with open(readme_html, "r") as html_file:
        html_content = html_file.read()

    parsed_html_content = parse_html(html_content)

    # Mark original <li> elements to identify which get added while tidying
    add_original_attribute(parsed_html_content, "li")

    # Some fixes are easier to apply before tidying/validating,
    # so errors are more obvious
    fix_incomplete_colgroups(parsed_html_content)
    fix_misplaced_list_content_wrappers(parsed_html_content)

    html_content, errors = validate_html(str(parsed_html_content))
    errors = errors.strip().split("\n")
    parsed_html_content = parse_html(html_content)

    if output_folder:
        readme_md = Path(output_folder, f"{connector_name}-{README_MD_NAME}")
        readme_html = Path(output_folder,
                           f"{connector_name}-{README_HTML_NAME}")
    else:
        readme_md = Path(connector_path, README_MD_NAME)

    new_path = None
    if not overwrite and readme_md.is_file():
        new_path = Path(readme_md.parent, README_MD_ORIGINAL_NAME)
        print(f"Backing-up original readme ({readme_md}) to: {new_path}")
        readme_md.rename(new_path)

    # Some fixes are better applied after tidying/validating
    remove_double_bullets(parsed_html_content)
    remove_original_attribute(parsed_html_content, "li")
    fix_relative_links(parsed_html_content, connector_path, "a", "href")
    fix_relative_links(parsed_html_content, connector_path, "img", "src")
    html_content = parsed_html_content.prettify(formatter="html")

    # HTML comments won't automatically make it into the markdown, but
    # we can't lose them because there are license/copyright statements
    comments = get_html_comments(parsed_html_content)
    md_comments = generate_md_comments(comments)

    md_content = html_to_md(html_content)
    md_content = md_content.replace("<div>","").replace("</div>","")
    md_content = md_content.replace("\\|", "|")
    with open(readme_md, "w") as md_file:
        num_chars_written = md_file.write(md_comments)
        num_chars_written += md_file.write(md_content)

    # To check how successful the conversion was, we'll get some stats about
    # the original and converted documents
    rendered_markdown = md_to_html(md_content)
    parsed_rendered_markdown = parse_html(rendered_markdown)

    _, original_word_count, original_words = \
        calculate_html_stats(parsed_html_content)
    _, converted_word_count, converted_words = \
        calculate_html_stats(parsed_rendered_markdown)

    parsed_json = get_app_json(connector_path)
    written_info = {
        "word_diff": converted_word_count - original_word_count,
        "original_words": original_words,
        "converted_words": converted_words,
        "app_name": parsed_json["name"],
        "folder": connector_name,
        "app_guid": parsed_json["appid"],
        "version": parsed_json["app_version"],
        "html_length": len(html_content),
        "md_length": num_chars_written,
        "errors": len(errors)
    }

    # When there are differences detected between original and converted
    # documents, a human will need to diff them
    if debug_mode:
        save_word_lists(readme_md, original_words, converted_words)
        save_text(readme_html, ".validated.html", html_content)

    return (written_info, new_path)


def main():
    parser = argparse.ArgumentParser(description=("Generate README.md files "
                                                  "from readme.html files in "
                                                  "SOAR apps"))
    parser.add_argument("--folder", dest="folder", required=True,
                        help="The top-level folder to process")
    parser.add_argument("--output", dest="output_folder",
                        help="Where to store generated markdown files")
    parser.add_argument("--debug", dest="debug", help="Enables debug mode")
    parser.add_argument("--overwrite", dest="overwrite",
                        help="If True, will overwrite output markdown file")
    parser.add_argument("--show-stats", dest="show_stats", default=False,
                        help="If True, will display stats")
    args = parser.parse_args()
    top_folder = args.folder
    output_folder = args.output_folder
    debug_mode = args.debug == "True"
    overwrite = args.overwrite == "True"
    show_stats = args.show_stats == "True"

    all_writes = {}
    all_skips = []
    all_backups = []
    folders = [f for f in os.listdir(top_folder)
               if os.path.isdir(Path(top_folder, f))]
    for folder in folders:
        folder_path = Path(top_folder, folder)

        (conversion_result, backup) = readme_html_to_markdown(folder_path,
                                                              folder,
                                                              output_folder,
                                                              overwrite,
                                                              debug_mode)
        if conversion_result:
            if backup:
                all_backups.append(backup)

            all_writes[conversion_result["app_guid"]] = conversion_result

            # Progress indicator
            print(".", end="", flush=True)
        else:
            all_skips.append(folder_path)

            # Progress indicator
            print("X", end="", flush=True)

    print(f"\n\nCouldn't find {len(all_skips)} html files")
    print(f"Backed-up the following {len(all_backups)} files:")
    print("\n".join([str(p) for p in all_backups]))
    print(f"Created {len(all_writes)} markdown files")

    if show_stats:
        sorted_writes = {k: v for k, v in sorted(all_writes.items(),
                         key=lambda item: abs(item[1]["word_diff"]),
                         reverse=True)}
        print("Stats:")
        for (i, (wk, wv)) in enumerate(sorted_writes.items()):
            wv["original_words"] = len(wv["original_words"])
            wv["converted_words"] = len(wv["converted_words"])
            print(", ".join([str(v) for k, v in wv.items()]))


if __name__ == "__main__":
    main()
