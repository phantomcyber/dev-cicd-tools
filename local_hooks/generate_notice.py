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
import shutil
import sys
from pathlib import Path
from packaging.version import Version
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
import toml
from local_hooks.helpers import find_uv_lock_file


# pip-licenses is used to query all python packages for license information
PYTHON_LICENSE_COMMAND = "pip-licenses"
PYTHON_LICENSE_COMMAND_ARGS = [
    "--format=json",
    "--with-license-file",
    "--no-license-path",
    "--with-urls",
    "--with-notice-file",
]

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


LEGACY_VCS_NAME = re.compile(r"\s+#(?P<name>[A-Za-z0-9_.-]+)=[^\s]+\s*$")
VCS_EGG_NAME = re.compile(r"[#&]egg=(?P<name>[A-Za-z0-9_.-]+)(?:&|$)")


def get_requirement_name(line: str) -> Optional[str]:
    """Return the distribution name represented by one requirements line."""
    requirement_text = line.strip()
    if not requirement_text or requirement_text.startswith("#"):
        return None

    if legacy_match := LEGACY_VCS_NAME.search(line):
        return canonicalize_name(legacy_match.group("name"))
    if egg_match := VCS_EGG_NAME.search(requirement_text):
        return canonicalize_name(egg_match.group("name"))

    # Whitespace starts an inline comment in requirements files. Preserve URL
    # fragments by only splitting on whitespace followed by '#'.
    requirement_text = re.split(r"\s+#", requirement_text, maxsplit=1)[0].strip()
    try:
        return canonicalize_name(Requirement(requirement_text).name)
    except InvalidRequirement:
        logging.error("Unable to extract package from requirement: %s", line.rstrip())
        return None


def get_package_dependencies(requirements_path: Path) -> list[str]:
    """
    Extract package names from the app requirements file.
    """
    if not requirements_path.is_file():
        logging.info("No requirements file found at %s", requirements_path)
        return []

    packages = []
    with open(requirements_path) as reqs:
        for line in reqs:
            if package := get_requirement_name(line):
                packages.append(package)
                logging.info("Found package: %s", package)
    return packages


def get_uv_tool_command() -> Optional[list[str]]:
    if shutil.which("uvx"):
        return ["uvx"]
    if shutil.which("uv"):
        return ["uv", "tool", "run"]
    return None


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    logging.debug("Running command: %s", shlex.join(command))
    return subprocess.run(command, capture_output=True, text=True)


def load_license_info(command: list[str]) -> list[dict]:
    result = run_command(command)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: {shlex.join(command)}"
        )
    return json.loads(result.stdout)


def load_license_info_with_uvx(packages: list[str], requirements_path: Path) -> list[dict]:
    uv_tool_command = get_uv_tool_command()
    if uv_tool_command is None:
        raise FileNotFoundError("uvx or uv is not available")

    return load_license_info(
        [
            *uv_tool_command,
            "--with-requirements",
            str(requirements_path),
            PYTHON_LICENSE_COMMAND,
            *PYTHON_LICENSE_COMMAND_ARGS,
            "--packages",
            *packages,
        ]
    )


def load_license_info_with_pip(packages: list[str], requirements_path: Path) -> list[dict]:
    pip_check = run_command([sys.executable, "-m", "pip", "--version"])
    if pip_check.returncode != 0:
        raise RuntimeError(
            f"uvx/uv is not available and pip is not importable from {sys.executable}"
        )

    install_command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "pip-licenses",
        "-r",
        str(requirements_path),
    ]
    install_result = run_command(install_command)
    if install_result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {install_result.returncode}: "
            f"{shlex.join(install_command)}"
        )

    return load_license_info(
        [
            sys.executable,
            "-m",
            "piplicenses",
            *PYTHON_LICENSE_COMMAND_ARGS,
            "--packages",
            *packages,
        ]
    )


def get_license_info_list(packages: list[str], requirements_path: Path) -> list[dict]:
    try:
        return load_license_info_with_uvx(packages, requirements_path)
    except (FileNotFoundError, RuntimeError) as uv_error:
        logging.warning("uvx pip-licenses failed; falling back to pip: %s", uv_error)

    return load_license_info_with_pip(packages, requirements_path)


def get_python_license_info(packages: list[str], requirements_path: Path):
    """
    Generate a series of LicenseLine objects describing every python dependency
    in the current environment.

    This uses the tool pip-licenses to automatically collect all package
    information by grabbing all packages in the current environment.
    """
    # A very large json array is returned. Missing values are marked 'UNKNOWN'
    license_info_list = get_license_info_list(packages, requirements_path)
    found_packages = {canonicalize_name(info.get("Name", "")) for info in license_info_list}
    missing_packages = {canonicalize_name(package) for package in packages} - found_packages
    if missing_packages:
        raise RuntimeError(
            "pip-licenses did not return license information for: "
            f"{', '.join(sorted(missing_packages))}"
        )

    for license_info in license_info_list:
        if license_info.get("Name") not in EXCLUDED_PYTHON_PACKAGES:
            logging.info(f"Found license information for {license_info.get('Name')}")
            yield LicenseLine.make_from_pip_json(license_info)


def get_app_json(connector_path: Path) -> tuple[str, str]:
    """
    Get the app name and license from the app.json file.
    """
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

    # Rewrite the file with cleaned content and exactly one terminal newline.
    # The preceding whitespace pass can leave the final content line already
    # newline-terminated, so writelines() followed by write("\n") would create
    # a blank line and make the hook non-idempotent.
    with open(notice_file_path, "w") as f:
        f.write("".join(lines).rstrip("\n") + "\n")


def get_sdk_version_from_lock(uv_lock_path: Path) -> Optional[Version]:
    """
    Return the resolved version of splunk-soar-sdk from the uv.lock file,
    or None if it is not present.
    """
    with open(uv_lock_path) as f:
        lock_data = toml.load(f)

    for package in lock_data.get("package", []):
        if package.get("name") == "splunk-soar-sdk":
            return Version(package["version"])
    return None


def main():
    """
    Generate a NOTICE file.

    This will extract license information from our python distribution
    """
    logging.getLogger().setLevel(logging.INFO)
    args = parse_args()
    connector_path = Path(args.connector_path)

    uv_lock_path = find_uv_lock_file(connector_path)

    if uv_lock_path:
        sdk_version = get_sdk_version_from_lock(uv_lock_path)
        if sdk_version is None or sdk_version < Version("3.20.0"):
            found = str(sdk_version) if sdk_version else "not installed"
            raise RuntimeError(
                f"splunk-soar-sdk >= 3.20.0 is required for NOTICE generation in SDK apps "
                f"(found: {found}). Please upgrade your SDK."
            )
        logging.info(
            "splunk-soar-sdk %s >= 3.20.0, delegating NOTICE generation to SDK", sdk_version
        )
        subprocess.run(
            ["uv", "run", "soarapps", "manifests", "create-notice"],
            cwd=uv_lock_path.parent,
            check=True,
        )
        return

    app_name, app_license = get_app_json(connector_path)
    notice_file_path = connector_path / "NOTICE"
    logging.info("Creating NOTICE file at %s", Path(notice_file_path.resolve()))

    with open(notice_file_path, "w") as f:
        # Write base license file
        f.write(f"Splunk SOAR App: {app_name}\n{app_license}\n")

        # Get all python package dependencies
        requirements_path = connector_path / "requirements.txt"
        packages = get_package_dependencies(requirements_path)
        valid_packages = [
            package for package in packages if package not in EXCLUDED_PYTHON_PACKAGES
        ]
        if valid_packages:
            f.write("Third Party Software Attributions:\n")
        else:
            return

        # Get license info for all package dependencies
        for item in get_python_license_info(
            packages=valid_packages, requirements_path=requirements_path
        ):
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
