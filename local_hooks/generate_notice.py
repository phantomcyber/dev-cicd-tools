#!/usr/bin/env python

import os
import json
import subprocess
import shlex
import re
from dataclasses import dataclass
from typing import Optional
import glob
import argparse
import dataclasses
import logging
from pathlib import Path
import toml
from local_hooks.helpers import find_uv_lock_file


# pip-licenses is used to query all python packages for license information
PYTHON_LICENSE_COMMAND = "pip-licenses"
PYTHON_LICENSE_COMMAND_ARGS = (
    "--format=json --with-license-file --no-license-path --with-urls --with-notice-file"
)

# A set of python packages that we've either already covered in the base
# license files, or don't actually use.
EXCLUDED_PYTHON_PACKAGES = set(
    [
        "2to3",  # Covered by Python license in base files
        "distro-info",  # No uses found
        "inspect-it",  # No uses found
        "language-selector",  # No uses found
        "pyjwkest",  # Subdep of Beaker - no need to attribute and it causes problems
        "python-apt",  # No uses found
        "python-debian",  # No uses found
        "yapf",  # Covered in base license file
        "beautifulsoup4",  # The below are built into SOAR and covered in base license file
        "soupsieve",
        "parse",
        "python_dateutil",
        "six",
        "requests",
        "certifi",
        "charset_normalizer",
        "idna",
        "urllib3",
        "sh",
        "xmltodict",
    ]
)

# This looks nice and cleanly seperates each block of license information.
LINE_SEPARATOR = "@@@@============================================================================"


@dataclasses.dataclass
class BuildDocsArgs:
    connector_path: Path


@dataclass
class LicenseLine:
    """
    This class represents a single block of license information.
    """

    package_name: str
    license_name: str
    license_text: str
    notice_text: Optional[str]
    version: str
    url: str

    @staticmethod
    def make_from_pip_json(pip_json):
        """
        Make a LicenseLine from information about a particular python package.
        """
        package_name = pip_json.get("Name")
        license_name = pip_json.get("License")
        license_text = pip_json.get("LicenseText")
        if license_text == "UNKNOWN":
            license_text = None
        version = pip_json.get("Version")
        url = pip_json.get("URL")

        notice_text = pip_json.get("NoticeText")

        # NOTICE files are rarely used, and only appear in Apache v2 projects.
        if notice_text == "UNKNOWN":
            notice_text = None

        return LicenseLine(package_name, license_name, license_text, notice_text, version, url)

    def write_line(self, f):
        """
        Write all license information into the file `f`.

        It's a good idea to have `f` opened in append mode.
        """

        if self.license_text is None:
            self.license_text = f"Please navigate to {self.url} to obtain a copy of the license."

        notice_text = ""
        if self.notice_text:
            notice_text = f"\nNotice:\n\n{self.notice_text}"

        format_list = [
            "\n",
            LINE_SEPARATOR,
            "\n\n",
            f"Library: {self.package_name} - {self.version}\n",
            f"Homepage: {self.url}\n",
            f"License: {self.license_name}\n",
            "License Text:\n\n",
            self.license_text,
            notice_text,
            "\n",
        ]

        for line in format_list:
            f.write(line)


def get_package_dependencies() -> list[str]:
    """
    Enter the virtual environment for the current project.

    This is necessary to ensure that the correct python packages are
    being used.
    """
    subprocess.run(["pip", "install", "pip-licenses"], capture_output=True).stdout
    subprocess.run(["pip", "install", "-r", "requirements.txt"], capture_output=True).stdout
    packages = []
    with open("requirements.txt") as reqs:
        for line in reqs:
            if match := re.match(r"^(.*?)(?=[=<>])", line):
                packages.append(match.group(0))
                logging.info(f"Found package: {match.group(0)}")
            else:
                print(f"ERROR extracting package from line: {line}")
    return packages


def get_python_license_info(packages: list[str]):
    """
    Generate a series of LicenseLine objects describing every python dependency
    in the current environment.

    This uses the tool pip-licenses to automatically collect all package
    information by grabbing all packages in the current environment.
    """
    command = shlex.split(
        f"{PYTHON_LICENSE_COMMAND} {PYTHON_LICENSE_COMMAND_ARGS} --packages {' '.join(packages)}"
    )
    license_info_proc = subprocess.run(command, capture_output=True).stdout

    # A very large json array is returned. Missing values are marked 'UNKNOWN'
    license_info_list = json.loads(license_info_proc)

    for license_info in license_info_list:
        if license_info.get("Name") not in EXCLUDED_PYTHON_PACKAGES:
            logging.info(f"Found license information for {license_info.get('Name')}")
            yield LicenseLine.make_from_pip_json(license_info)


def get_app_json(connector_path: Path, uv_lock_path: Optional[Path]) -> tuple[str, str]:
    """
    Get the app name and license from the app.json file.
    """

    if uv_lock_path:
        with open(uv_lock_path / "pyproject.toml") as f:
            toml_data = toml.load(f)
            app_name = toml_data.get("project", {}).get("name")
            app_license = toml_data.get("project", {}).get("license")
            return app_name, app_license

    logging.info("Looking for app JSON in: %s", connector_path)
    json_files = glob.glob(os.path.join(connector_path, "*.json"))
    # Exclude files with the pattern '*.postman_collection.json'
    filtered_json_files = [
        file for file in json_files if not file.endswith(".postman_collection.json")
    ]
    if len(filtered_json_files) != 1:
        print(filtered_json_files)
        raise ValueError(f"Expected 1 json file, found {len(filtered_json_files)}")

    # Read the app json and extact the name and license
    json_file_path = filtered_json_files[0]
    with open(json_file_path) as f:
        app_keys = json.load(f)
        app_name = app_keys["name"]
        app_license = app_keys["license"]

    logging.info("Found app JSON: %s", json_file_path)
    if not app_name or not app_license:
        raise ValueError("App name or license not found in app.json")
    return app_name, app_license


def remove_trailing_whitespace(notice_file_path: Path):
    """
    Remove all trailing whitespace from the NOTICE
    """
    logging.info("Removing trailing whitespace from NOTICE file")
    with open(notice_file_path) as f:
        lines = f.readlines()

    # Strip trailing whitespace from each line
    trimmed_lines = [line.rstrip() for line in lines]

    # Write the cleaned lines back to the file
    with open(notice_file_path, "w") as f:
        f.write("\n".join(trimmed_lines))


def remove_trailing_blank_lines(notice_file_path: Path):
    """
    Remove all trailing blank lines from the NOTICE
    """
    logging.info("Removing trailing blank lines from NOTICE file")
    with open(notice_file_path) as f:
        lines = f.readlines()

    # Remove trailing blank lines
    while lines and lines[-1].strip() == "":
        lines.pop()

    # Rewrite the file with cleaned content
    with open(notice_file_path, "w") as f:
        f.writelines(lines)
        # Ensure there's a single newline at the end of the file
        f.write("\n")


def get_sdkfied_app_dependencies(pyproject_toml_path: Path) -> list[str]:
    """
    Get the dependencies from the pyproject.toml file.
    """
    with open(pyproject_toml_path) as f:
        toml_data = toml.load(f)

    return toml_data.get("project", {}).get("dependencies", [])


def main():
    """
    Generate a NOTICE file.

    This will extract license information from our python distribution
    """
    logging.getLogger().setLevel(logging.INFO)
    args = parse_args()
    connector_path = Path(args.connector_path)

    uv_lock_path = find_uv_lock_file(connector_path)
    app_name, app_license = get_app_json(connector_path, uv_lock_path.parent)
    notice_file_path = connector_path / "NOTICE"
    logging.info("Creating NOTICE file at %s", Path(notice_file_path.resolve()))

    with open(notice_file_path, "w") as f:
        # Write base license file
        f.write(f"Splunk SOAR App: {app_name}\n{app_license}\n")

        # Get all python package dependencies
        if uv_lock_path:
            uv_lock_dir = uv_lock_path.parent
            packages = get_sdkfied_app_dependencies(uv_lock_dir / "pyproject.toml")
        else:
            packages = get_package_dependencies()
        valid_packages = [
            package for package in packages if package not in EXCLUDED_PYTHON_PACKAGES
        ]
        if valid_packages:
            f.write("Third Party Software Attributions:\n")
        else:
            return

        # Get license info for all package dependencies
        for item in get_python_license_info(packages=valid_packages):
            item.write_line(f)

    remove_trailing_whitespace(notice_file_path)
    remove_trailing_blank_lines(notice_file_path)


def parse_args() -> BuildDocsArgs:
    help_str = " ".join(line.strip() for line in (__doc__ or "").strip().splitlines())
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument("connector_path", help="Path to the connector", type=Path)
    return BuildDocsArgs(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
