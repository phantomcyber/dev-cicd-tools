"""
Builds connector detail documentation similar to
https://my.phantom.us/<soar_version>/docs/app_reference/<connector>,
in github-flavored markdown format, and combines it with human-written
author notes (legacy README.md).
"""

import argparse
import dataclasses
import datetime
import logging
import re
from pathlib import Path
from collections.abc import Iterator
from typing import Any, Optional, overload

import mdformat
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.ext import Extension
from jinja2.lexer import Token, TokenStream

from local_hooks.build_docs_lib import get_app_json, generate_gh_fragment

SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATE_DIR = SCRIPT_DIR / "templates"
TEMPLATE_NAME = "connector_detail.md.j2"
README_OUTPUT_NAME = "README.md"
MANUAL_README_CONTENT_FILE_NAME = "manual_readme_content.md"
README_INPUT_NAME = README_OUTPUT_NAME
DEFAULT_ENCODING = "utf-8"

# From https://enterprise.github.com/downloads/en/markdown-cheatsheet.pdf
MARKDOWN_RESERVED_CHARACTERS = [
    "\\",
    "`",
    "*",
    "_",
    "{",
    "}",
    "[",
    "]",
    "(",
    ")",
    "#",
    "+",
    "-",
    ".",
    "!",
    "@",
    "|",
    ":",
]


class EscapeMDFilterVarsExtension(Extension):
    # Markdown in all unfiltered injected values should be escaped
    def filter_stream(self, stream: TokenStream) -> Iterator[Token]:
        prev_token = None
        for token in stream:
            if token.type == "variable_end" and str(prev_token) not in self.environment.filters:
                yield Token(token.lineno, "pipe", "|")
                yield Token(token.lineno, "name", "escape_markdown")
            yield token
            prev_token = token


def generate_action_heading_text(text: str) -> str:
    return f"action: '{text}'"


@overload
def escape_markdown(data: dict[str, Any]) -> dict[str, Any]: ...


@overload
def escape_markdown(data: str) -> str: ...


def escape_markdown(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: escape_markdown(val) for key, val in data.items()}
    elif isinstance(data, str):
        return re.sub(r"([\\*])", r"\\\1", data)
    else:
        return data


def load_file(file_path: Path) -> Optional[str]:
    try:
        logging.info(f"Loading file: {file_path}")
        return file_path.read_text()
    except FileNotFoundError:
        logging.warning(f"Couldn't find file: {file_path}")

    return None


def render_docs(json_content: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        extensions=[EscapeMDFilterVarsExtension],
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["generate_gh_fragment"] = generate_gh_fragment
    env.filters["generate_action_heading_text"] = generate_action_heading_text
    env.filters["escape_markdown"] = escape_markdown

    logging.info(f"Rendering with template: {TEMPLATE_NAME} from {TEMPLATE_DIR}")
    t = env.get_template(TEMPLATE_NAME)
    return mdformat.text(t.render(connector=json_content, year=datetime.datetime.now().year))


def write_docs(output_readme_path: Path, content: str) -> bool:
    try:
        original = output_readme_path.read_text()
    except FileNotFoundError:
        original = ""

    if original == content:
        logging.info("Detected no readme updates")
        return False

    output_readme_path.write_text(content)
    logging.info(f"Saved readme as {output_readme_path}")
    return True


def build_docs(
    connector_path: Path, json_name: Optional[str] = None, app_version: Optional[str] = None
) -> dict[str, str]:
    json_content = get_app_json(connector_path, json_name)
    if app_version:
        json_content["app_version"] = app_version

    manual_docs = connector_path / MANUAL_README_CONTENT_FILE_NAME
    if manual_docs.is_file():
        json_content["md_content"] = manual_docs.read_text(encoding=DEFAULT_ENCODING)

    # If the entire asset configuration is meant to be hidden, don't render the config section at all
    include_config = any(
        field["data_type"] != "ph" and field.get("visibility", ["all"])
        for field in json_content.get("configuration", {}).values()
    )
    if not include_config:
        json_content.pop("configuration", None)

    content = render_docs(json_content)

    output_readme_path = connector_path / README_OUTPUT_NAME
    if write_docs(output_readme_path, content):
        return {output_readme_path.name: content}
    return {}


@dataclasses.dataclass
class BuildDocsArgs:
    connector_path: Path
    json_name: Optional[str] = None


def main() -> None:
    """
    Main entrypoint.
    """
    logging.getLogger().setLevel(logging.INFO)
    args = parse_args()
    connector_path = Path(args.connector_path)
    json_name = args.json_name
    if json_name is not None and not json_name.endswith(".json"):
        json_name = json_name + ".json"

    build_docs(connector_path, json_name=json_name)


def parse_args() -> BuildDocsArgs:
    help_str = " ".join(line.strip() for line in (__doc__ or "").strip().splitlines())
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument("connector_path", help="Path to the connector", type=Path)
    parser.add_argument("--json-name", help="JSON file name")
    return BuildDocsArgs(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
