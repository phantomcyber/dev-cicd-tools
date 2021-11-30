"""
Builds connector detail documentation similar to
https://my.phantom.us/<soar_version>/docs/app_reference/<connector>,
in github-flavored markdown format, and combines it with human-written
author notes (legacy readme.md).
"""
import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.ext import Extension
from jinja2.lexer import Token

from readme_to_markdown import (README_HTML_NAME, README_MD_ORIGINAL_NAME,
                                get_visible_text_from_html, md_to_html,
                                parse_html, readme_html_to_markdown)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIR = Path(SCRIPT_DIR, "templates")
TEMPLATE_NAME = "connector_detail.md"
README_OUTPUT_NAME = "readme.md"
README_INPUT_NAME = README_OUTPUT_NAME

# From https://enterprise.github.com/downloads/en/markdown-cheatsheet.pdf
MARKDOWN_RESERVED_CHARACTERS = ["\\", "`", "*", "_", "{", "}", "[", "]", "(",
                                ")", "#", "+", "-", ".", "!",  "@", "|", ":"]


class EscapeMDFilterVarsExtension(Extension):
    # Markdown in all unfiltered injected values should be escaped
    def filter_stream(self, stream):
        prev_token = None
        for token in stream:
            if (token.type == "variable_end"
                    and str(prev_token) not in self.environment.filters):
                yield Token(token.lineno, "pipe", "|")
                yield Token(token.lineno, "name", "escape_markdown")
            yield token
            prev_token = token


def generate_gh_fragment(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text)
    return re.sub(r"[\s]", "-", text)


def generate_action_heading_text(text):
    return f"action: '{text}'"


def escape_markdown(text):
    if isinstance(text, str):
        for reserved_char in MARKDOWN_RESERVED_CHARACTERS:
            text = text.replace(reserved_char, f"\\{reserved_char}")
    return text


def get_app_json(app_json_dir):
    logging.info("Looking for app JSON in: %s", app_json_dir)
    app_json_name = [f for f in os.listdir(app_json_dir)
                     if f.endswith(".json")
                     and "postman_collection" not in f][0]
    json_file_path = Path(app_json_dir, app_json_name)
    logging.info("Loading json: %s", app_json_name)
    with open(json_file_path, "r") as json_file:
        return json.load(json_file)


def load_file(file_path):
    try:
        logging.info("Loading file: %s", file_path)
        with open(file_path) as f:
            return f.read()
    except FileNotFoundError:
        logging.warning("Couldn't find file: %s", file_path)
    return None


def render_template_to_file(connector_path, json_content):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        extensions=[EscapeMDFilterVarsExtension],
        autoescape=select_autoescape()
    )
    env.filters["generate_gh_fragment"] = generate_gh_fragment
    env.filters["generate_action_heading_text"] = generate_action_heading_text
    env.filters["escape_markdown"] = escape_markdown

    logging.info("Rendering with template: %s from %s",
                 TEMPLATE_NAME, TEMPLATE_DIR)
    t = env.get_template(TEMPLATE_NAME)
    rendered_content = t.render(connector=json_content)

    output_readme_path = Path(connector_path, README_OUTPUT_NAME)
    logging.info("Saved readme as %s", output_readme_path)
    with open(output_readme_path, "w") as readme_file:
        readme_file.write(rendered_content)

    return rendered_content, output_readme_path


def build_docs(connector_path, app_version=None):
    input_readme_path = Path(connector_path, README_INPUT_NAME)

    json_content = get_app_json(connector_path)
    if app_version:
        json_content["app_version"] = app_version

    if md_content := load_file(input_readme_path):
        template_path = Path(TEMPLATE_DIR, TEMPLATE_NAME)
        with open(template_path) as template_file:
            first_line_in_template = template_file.readline()

        if first_line_in_template in md_content:
            raise ValueError("Input readme contains auto-generated content!")

    json_content["md_content"] = md_content

    return render_template_to_file(connector_path, json_content)


def manage_existing_markdown(connector_path):
    md_path = Path(connector_path, README_INPUT_NAME)
    author_notes_path = Path(connector_path, README_MD_ORIGINAL_NAME)

    # Does the readme exist?
    if not md_path.is_file():
        return None, None

    # Does notes.md already exist?
    if author_notes_path.is_file():
        logging.info("Removing existing auto-gen readme: %s", md_path)
        md_path.unlink(missing_ok=True)
        return None, None

    # Are the first N words of readme.md the same as the first N words
    # of readme.html (is md auto-generated)?
    with open(md_path) as md_file:
        md_content = md_file.read()

    html_path = Path(connector_path, README_HTML_NAME)
    if html_path.is_file():
        with open(html_path) as html_file:
            html_content = html_file.read()
        parsed_html_content = parse_html(html_content)

        txt_from_htm = get_visible_text_from_html(parsed_html_content).split()
        html_from_md = md_to_html(md_content)
        parsed_html_from_md = parse_html(html_from_md)
        txt_from_md = get_visible_text_from_html(parsed_html_from_md).split()

        if txt_from_htm[:50] == txt_from_md[:50]:
            logging.info("Removing existing auto-gen readme: %s", md_path)
            md_path.unlink()
            return None, None

    logging.info("Backing-up existing readme from %s to %s",
                 md_path, author_notes_path)
    return md_content, md_path.rename(author_notes_path)


def build_docs_from_html(connector_path, app_version=None):
    backup_content, backup_path = manage_existing_markdown(connector_path)
    readme_html_to_markdown(connector_path)
    output_content, output_path = build_docs(connector_path, app_version)

    updates = [(output_content, str(output_path.relative_to(connector_path)))]
    if backup_content:
        updates.append((backup_content, str(backup_path.relative_to(connector_path))))

    return updates


def main(args):
    """
    Main entrypoint.
    """
    connector_path = args.connector_path
    from_html = args.from_html  == "True"
    if from_html:
        build_docs_from_html(connector_path)
    else:
        build_docs(connector_path)


def parse_args():
    help_str = " ".join(line.strip() for line in __doc__.strip().splitlines())
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument("connector_path", help="Path to the connector")
    parser.add_argument("from_html", nargs='?', default=False,
                        help="Build from html instead of md")
    return parser.parse_args()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(parse_args()))
