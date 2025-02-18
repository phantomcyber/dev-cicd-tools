# More advanced copyright updates
# Accurately replaces years
# Adds header to files that don't have one
# Updates connector json license as well
# - Python files
# - HTML files
# - JSON files
# - Text files
# - NOTICE files
# - LICENSE files/generation

import os
import re
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
JINJA_ENV = Environment(loader=FileSystemLoader(os.path.join(SCRIPT_DIR, "templates")))
LICENSE_TEMPLATE = JINJA_ENV.get_template("LICENSE.j2")


def generate_apache_license_content(copyright_str: str) -> str:
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


def get_apache_header(copyright_str: str, extension: str) -> str:
    current_year = datetime.now().year
    updated_copyright = f"Copyright (c) {current_year} {copyright_str}"

    # Define comment markers based on file type
    if extension in [".py", ".txt"]:
        start, mid, end = "#", "#", ""
    elif extension == ".html":
        start, mid, end = "<!--\n", "", "\n-->"
    elif extension == ".json":
        start, mid, end = "/*\n", " *", "\n*/"
    else:  # NOTICE, LICENSE, and other files
        start, mid, end = "", "", ""

    lines = [
        f"{mid} {updated_copyright}",
        f"{mid}",
        f'{mid} Licensed under the Apache License, Version 2.0 (the "License");',
        f"{mid} you may not use this file except in compliance with the License.",
        f"{mid} You may obtain a copy of the License at",
        f"{mid}",
        f"{mid}     http://www.apache.org/licenses/LICENSE-2.0",
        f"{mid}",
        f"{mid} Unless required by applicable law or agreed to in writing, software",
        f'{mid} distributed under the License is distributed on an "AS IS" BASIS,',
        f"{mid} WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.",
        f"{mid} See the License for the specific language governing permissions and",
        f"{mid} limitations under the License.",
    ]

    lines = [f"{line}" if mid.strip() else line for line in lines]
    return f"{start}{chr(10).join(lines)}{end}\n\n"


def update_file_copyright(file_path: Path, copyright_str: str) -> bool:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    # Special handling for connector json license
    if file_path.suffix == ".json":
        import json

        try:
            with open(file_path) as f:
                data = json.load(f)

            if "license" in data:
                match = COPYRIGHT_REGEX.match(data["license"])
                if match:
                    updated_copyright = update_copyright_years(match.group("copyright"))
                    if updated_copyright != match.group("copyright"):
                        data["license"] = updated_copyright
                        with open(file_path, "w") as f:
                            json.dump(data, f, indent=4)
                        return True
                return False

        except json.JSONDecodeError:
            pass

    # Normal processing for non-JSON files
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


def update_copyrights(app_dir: str, copyright_str: str) -> dict[str, str]:
    updated_files = {}

    # Handle LICENSE file specially (generation)
    license_path = Path(app_dir, "LICENSE")
    if license_path.is_file():
        if update_file_copyright(license_path, copyright_str):
            updated_files["LICENSE"] = license_path.read_text()
    else:
        license_content = generate_apache_license_content(copyright_str)
        license_path.write_text(license_content)
        updated_files["LICENSE"] = license_content

    # All other files check
    for root, _, files in os.walk(app_dir):
        for file in files:
            if file == "LICENSE":
                continue

            file_path = Path(root, file)
            relative_path = str(file_path.relative_to(app_dir))

            if (
                not any(file.endswith(ext) for ext in SUPPORTED_SOURCE_FILE_EXTENSIONS)
                and file not in SUPPORTED_SOURCE_FILE_EXTENSIONS
            ):
                continue

            if update_file_copyright(file_path, copyright_str):
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
