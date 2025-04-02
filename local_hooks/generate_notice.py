#!/usr/bin/env python

import os
import json
import subprocess
import shlex
import re
from dataclasses import dataclass
from typing import Optional
import glob

THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
NOTICE_FILE_PATH = f"{THIS_DIRECTORY}/NOTICE"

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
            yield LicenseLine.make_from_pip_json(license_info)


def get_app_json() -> tuple[str, str]:
    """
    Get the app name and license from the app.json file.
    """
    # Find all .json files in the current directory
    json_files = glob.glob(os.path.join(THIS_DIRECTORY, "*.json"))
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

    return app_name, app_license


def remove_trailing_blank_lines():
    """
    Remove all trailing blank lines from the NOTICE
    """
    with open(NOTICE_FILE_PATH) as f:
        lines = f.readlines()

    # Remove trailing blank lines
    while lines and lines[-1].strip() == "":
        lines.pop()

    # Rewrite the file with cleaned content
    with open(NOTICE_FILE_PATH, "w") as f:
        f.writelines(lines)


def main():
    """
    Generate a NOTICE file.

    This will extract license information from our python distribution
    """

    app_name, app_license = get_app_json()

    with open(NOTICE_FILE_PATH, "w") as f:
        # Write base license file
        f.write(f"Splunk SOAR App: {app_name}\n{app_license}\n")

        # Get all python package dependencies
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

    remove_trailing_blank_lines()


if __name__ == "__main__":
    main()
