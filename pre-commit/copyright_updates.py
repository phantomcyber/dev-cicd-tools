import os
import re
import tokenize
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
import json

from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
JINJA_ENV = Environment(loader=FileSystemLoader(os.path.join(SCRIPT_DIR, "templates")))
LICENSE_TEMPLATE = JINJA_ENV.get_template("LICENSE.j2")


def generate_apache_license_content(copyright_str: str) -> str:
    # First update the years in the copyright string
    match = COPYRIGHT_REGEX.match(copyright_str)
    if match:
        copyright_str = update_copyright_years(match.group("copyright"))
    return f"{LICENSE_TEMPLATE.render(copyright=copyright_str)}\n"


SUPPORTED_SOURCE_FILE_EXTENSIONS = (".py", ".html", ".json", ".txt", "NOTICE", "LICENSE")

COPYRIGHT_REGEX = re.compile(
    r"^#*\s*(?P<copyright>Copyright\s*(\(c\))?\s*(([0-9]{4},?)+(-[0-9]{4})?)?,?\s*[a-z0-9.,\s]+"
    r",?\s*(([0-9]{4},?)+(-[0-9]{4})?)?)$",
    re.IGNORECASE,
)


def update_copyright_years(copyright_match: str) -> str:
    current_year = str(datetime.now().year)
    years = re.findall(r"(\d{4})", copyright_match)
    if not years:
        return copyright_match

    start_year = years[0]
    if len(years) > 1:
        end_year = years[-1]
        if end_year != current_year:
            return re.sub(r"\d{4}-\d{4}", f"{start_year}-{current_year}", copyright_match)
        return copyright_match

    if start_year == current_year:
        return copyright_match

    return re.sub(r"\d{4}", f"{start_year}-{current_year}", copyright_match)


def update_text_file_copyright(file_path: Path, copyright_str: str) -> bool:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    updated = False
    updated_lines = []

    with open(file_path) as f:
        lines = f.readlines()

    for line in lines:
        match = COPYRIGHT_REGEX.match(line)
        if match:
            updated_copyright = update_copyright_years(match.group("copyright"))
            new_line = line.replace(match.group("copyright"), updated_copyright)
            if new_line != line:
                updated = True
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)

    if updated:
        with open(file_path, "w") as f:
            f.writelines(updated_lines)

    return updated


def update_python_file_copyright(file_path: Path, copyright_str: str) -> bool:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    replaced_lines = {}
    with open(file_path, "rb") as src:
        tokens = tokenize.tokenize(src.readline)
        for comment in (t for t in tokens if t.type == tokenize.COMMENT):
            match = COPYRIGHT_REGEX.match(comment.line)
            if match:
                line_number = comment.start[0] - 1
                updated_copyright = update_copyright_years(match.group("copyright"))
                new_comment = comment.line.replace(match.group("copyright"), updated_copyright)
                if new_comment.strip() != comment.line.strip():
                    replaced_lines[line_number] = new_comment

    if not replaced_lines:
        return False

    with open(file_path, "r+") as f:
        original_lines = f.readlines()
        f.seek(0)
        f.truncate()
        for i in range(len(original_lines)):
            if i in replaced_lines:
                f.write(replaced_lines[i])
            else:
                f.write(original_lines[i])
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
                updated_copyright = update_copyright_years(match.group("copyright"))
                new_comment = comment_lines[i].replace(match.group("copyright"), updated_copyright)
                if new_comment == comment_lines[i]:
                    continue
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


def update_json_file_copyright(file_path: Path, copyright_str: str) -> bool:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    try:
        with open(file_path) as f:
            data = json.load(f)

        if "license" in data:
            match = COPYRIGHT_REGEX.match(data["license"])
            if match:
                updated_copyright = update_copyright_years(match.group("copyright"))
                if updated_copyright != data["license"]:
                    with open(file_path) as f:
                        content = f.read()
                    # Replace license string
                    updated_content = content.replace(data["license"], updated_copyright)
                    with open(file_path, "w") as f:
                        f.write(updated_content)
                    return True
    except json.JSONDecodeError:
        return False

    return False


def update_copyrights(app_dir: str, copyright_str: str) -> dict[str, str]:
    updated_files = {}

    # Handle LICENSE file specially
    license_path = Path(app_dir, "LICENSE")
    if license_path.is_file():
        # First try to update existing copyright in LICENSE
        if update_text_file_copyright(license_path, copyright_str):
            updated_files["LICENSE"] = license_path.read_text()
    else:
        # Only use template for new LICENSE files
        license_content = generate_apache_license_content(copyright_str)
        license_path.write_text(license_content)
        updated_files["LICENSE"] = license_content

    for root, _, files in os.walk(app_dir):
        for file in files:
            if file == "LICENSE":
                continue  # Handled above

            file_path = Path(root, file)
            relative_path = str(file_path.relative_to(app_dir))

            if (
                not any(file.endswith(ext) for ext in SUPPORTED_SOURCE_FILE_EXTENSIONS)
                and file not in SUPPORTED_SOURCE_FILE_EXTENSIONS
            ):
                continue

            if file.endswith(".py"):
                if update_python_file_copyright(file_path, copyright_str):
                    updated_files[relative_path] = file_path.read_text()
            elif file.endswith(".html"):
                if update_html_file_copyright(file_path, copyright_str):
                    updated_files[relative_path] = file_path.read_text()
            elif file.endswith(".json"):
                if update_json_file_copyright(file_path, copyright_str):
                    updated_files[relative_path] = file_path.read_text()
            else:
                if update_text_file_copyright(file_path, copyright_str):
                    updated_files[relative_path] = file_path.read_text()

    return updated_files


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: copyright_updates.py <directory>")
        sys.exit(1)

    app_dir = sys.argv[1]
    copyright_str = "Copyright (c) Splunk Inc."
    update_copyrights(app_dir, copyright_str)
