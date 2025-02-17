import os
import re
import tokenize
from html.parser import HTMLParser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
JINJA_ENV = Environment(loader=FileSystemLoader(os.path.join(SCRIPT_DIR, "templates")))
LICENSE_TEMPLATE = JINJA_ENV.get_template("LICENSE.j2")


def generate_apache_license_content(copyright_str: str) -> str:
    return f"{LICENSE_TEMPLATE.render(copyright=copyright_str)}\n"


SUPPORTED_SOURCE_FILE_EXTENSIONS = (".py", ".html")

COPYRIGHT_REGEX = re.compile(
    r"^#*\s*(?P<copyright>Copyright\s*(\(c\))?\s*(([0-9]{4},?)+(-[0-9]{4})?)?,?\s*[a-z0-9.,\s]+"
    r",?\s*(([0-9]{4},?)+(-[0-9]{4})?)?)$",
    re.IGNORECASE,
)


def update_python_file_copyright(file_path: Path, copyright_str: str) -> bool:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    replaced_lines = {}

    with open(file_path, "rb") as src:
        tokens = tokenize.tokenize(src.readline)
        for comment in (t for t in tokens if t.type == tokenize.COMMENT):
            match = COPYRIGHT_REGEX.match(comment.line)
            if match:
                line_number = comment.start[0] - 1  # returned line numbers are 1-indexed
                new_comment = comment.line.replace(match.group("copyright"), copyright_str)
                if new_comment.strip() != comment.line.strip():
                    replaced_lines[line_number] = f"{new_comment}\n"

    if not replaced_lines:
        return False

    with open(file_path, "r+") as f:
        original_lines = f.readlines()
        f.seek(0)
        f.truncate()
        for i in range(len(original_lines)):
            f.write(replaced_lines.get(i, original_lines[i]))

    return True


class HtmlCopyrightProcessor(HTMLParser):
    def __init__(self, new_copyright_str):
        super().__init__()
        self.new_copyright_str = new_copyright_str
        self.updated_lines = {}

    def feed(self, data):
        self.updated_lines.clear()
        super().feed(data)
        return self.updated_lines

    def handle_comment(self, data):
        comment_lines = data.split("\n")
        for i in range(len(comment_lines)):
            match = COPYRIGHT_REGEX.match(comment_lines[i])
            if match:
                new_comment = comment_lines[i].replace(
                    match.group("copyright"), self.new_copyright_str
                )
                if new_comment == comment_lines[i]:
                    continue
                # Check if the comment immediately follows or precedes
                # the start/end of a comment
                if i == 0:
                    new_comment = f"<!--{new_comment}"
                elif i == len(comment_lines) - 1:
                    new_comment = f"{new_comment}-->"

                self.updated_lines[self.lineno - 1 + i] = new_comment


def update_html_file_copyright(file_path: Path, copyright_str: str) -> bool:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    original_lines = file_path.read_text().splitlines()
    if original_lines[-1] == "":
        original_lines = original_lines[:-1]

    processor = HtmlCopyrightProcessor(copyright_str)
    processor.feed("\n".join(original_lines))

    if not processor.updated_lines:
        return False

    with open(file_path, "w") as f:
        for i in range(len(original_lines)):
            f.write(f"{processor.updated_lines.get(i, original_lines[i])}\n")

    return True


def update_copyrights(app_dir: str, copyright_str: str) -> dict[str, str]:
    updated_files = {}

    license_content = generate_apache_license_content(copyright_str)
    license_path = Path(app_dir, "LICENSE")
    if license_path.is_file():
        if license_path.read_text() != license_content:
            updated_files["LICENSE"] = license_content
    else:
        updated_files["LICENSE"] = license_content

    for py_file in Path(app_dir).rglob("*.py"):
        if update_python_file_copyright(py_file, copyright_str):
            updated_files[str(py_file.relative_to(app_dir))] = py_file.read_text()

    for html_file in Path(app_dir).rglob("*.html"):
        if update_html_file_copyright(html_file, copyright_str):
            updated_files[str(html_file.relative_to(app_dir))] = html_file.read_text()

    return updated_files
