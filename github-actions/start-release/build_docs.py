"""
Builds connector detail documentation similar to
https://my.phantom.us/<soar_version>/docs/app_reference/<connector>,
in github-flavored markdown format, and combines it with human-written
author notes (legacy README.md).
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
README_OUTPUT_NAME = "README.md"
MANUAL_README_CONTENT_FILE_NAME = "manual_readme_content.md"
README_INPUT_NAME = README_OUTPUT_NAME
DEFAULT_ENCODING = "utf-8"

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


# def escape_markdown(text):
#     if isinstance(text, str):
#         for reserved_char in MARKDOWN_RESERVED_CHARACTERS:
#             text = text.replace(reserved_char, f"\\{reserved_char}")
#     return text

def escape_markdown(data):
    if isinstance(data, dict):
        return {key: escape_markdown(val) for key, val in data.items()}
    elif isinstance(data, str):
        return re.sub(r'([\\*])', r'\\\1', data)
    else:
        return data

def get_app_json(app_json_dir, json_name):
    logging.info("Looking for app JSON in: %s", app_json_dir)
    if not json_name:
        try:
            app_json_name = [f for f in os.listdir(app_json_dir)
                             if f.endswith(".json")
                             and "postman_collection" not in f][0]
        except IndexError:
            logging.error("Unable to find app JSON")
            sys.exit(1)
    else:
        if os.path.isfile(os.path.join(app_json_dir, f"{json_name}.json")):
            app_json_name = json_name
        else:
            logging.error("Provided JSON name does not exist")
            sys.exit(1)

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


def check_markdown_for_template_text(md_content):
    if md_content:
        template_path = Path(TEMPLATE_DIR, TEMPLATE_NAME)
        with open(template_path) as template_file:
            first_line_in_template = template_file.readline()

        return first_line_in_template in md_content

def build_docs(connector_path, json_name=None, app_version=None):
    connector_path = Path(connector_path)
    input_readme_path = Path(connector_path, README_INPUT_NAME)

    json_content = get_app_json(connector_path, json_name)
    if app_version:
        json_content["app_version"] = app_version

    md_content = load_file(input_readme_path)
    if md_content and not check_markdown_for_template_text(md_content):
        json_content["md_content"] = md_content
    else:
        manual_readme_content_path = Path(connector_path, MANUAL_README_CONTENT_FILE_NAME)
        if manual_readme_content_path.is_file():
            json_content["md_content"] = manual_readme_content_path.read_text(encoding=DEFAULT_ENCODING)

    return render_template_to_file(connector_path, json_content)


def first_n_rendered_words_match_readme_html(n, connector_path, md_content):
    html_path = Path(connector_path, README_HTML_NAME)
    if html_path.is_file():
        with open(html_path) as html_file:
            html_content = html_file.read()
        parsed_html_content = parse_html(html_content)

        txt_from_htm = get_visible_text_from_html(parsed_html_content).split()
        html_from_md = md_to_html(md_content)
        parsed_html_from_md = parse_html(html_from_md)
        txt_from_md = get_visible_text_from_html(parsed_html_from_md).split()

        if txt_from_htm[:n] == txt_from_md[:n]:
            return True

    return False


def has_markdown_comment(md_content):
    return "[comment]: #" in md_content


def load_existing_markdown(connector_path):
    md_path = Path(connector_path, README_INPUT_NAME)

    if not md_path.is_file():
        return None

    with open(md_path) as md_file:
        return md_file.read()


def build_docs_from_html(connector_path, json_name=None, app_version=None):
    connector_path = Path(connector_path)
    original_content = load_existing_markdown(connector_path)
    readme_html_to_markdown(connector_path, overwrite=True, json_name=json_name)
    output_content, output_path = build_docs(connector_path, app_version)

    if original_content:
        original_content = original_content.replace('\r','')
    if output_content:
        output_content = output_content.replace('\r','')
    if original_content == output_content:
        logging.info('Detected no readme updates')
        return {}

    return {
        str(output_path.relative_to(connector_path)): output_content
    }


def main(args):
    """
    Main entrypoint.
    """
    connector_path = Path(args.connector_path)
    from_html = args.from_html == "True"
    json_name = args.json_name
    if from_html:
        build_docs_from_html(connector_path, json_name)
    else:
        build_docs(connector_path, json_name)


def parse_args():
    help_str = " ".join(line.strip() for line in __doc__.strip().splitlines())
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument("connector_path", help="Path to the connector")
    parser.add_argument("from_html", default=False, help="Build from html instead of md")
    parser.add_argument("json_name", default=None, type=str, nargs="?", help="JSON file name")
    return parser.parse_args()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(parse_args()))
