from typing import NamedTuple
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
import os
import shutil
import re

from urllib.parse import urlparse
import requests
from github import Github, Auth


APP_PATH = Path.cwd()
REQUIREMENTS_PATH = APP_PATH.joinpath("requirements.txt")
WHEEL_PATH = APP_PATH.joinpath("wheels")

TARGET_PYTHON = "3.9"
TARGET_PLATFORM = "manylinux2014_x86_64"

APP_JSON_INDENT = 4

# We don't want to include these wheels in bundled app packages, because SOAR already makes them
# available. Note that hyphens and underscores are synonymous when specifying a Python package in
# requirements.txt. However, the pip transaction will always use hyphens, so that's how we will
# refer to them here.
IGNORED_WHEELS = [
    "beautifulsoup4",
    "soupsieve",
    "parse",
    "python-dateutil",
    "six",
    "requests",
    "certifi",
    "charset-normalizer",
    "idna",
    "urllib3",
    "sh",
    "xmltodict",
]

# If one of these is included in requirements.txt, we want to add a specific warning about it.
# We can't remove it automatically, but we can suggest that the developer eliminate it.
# Again, if hyphens or underscores come into play, we'll always use hyphens here.
WARN_WHEELS = {
    "simplejson": (
        "This package is not needed, as JSON support has been built into Python since "
        "version 2.6. `simplejson` also includes binary components that break compatibility "
        "between minor Python versions. To reduce complexity, consider removing it and using the "
        "built-in `json` library."
    ),
}


@dataclass
class AppJson:
    path: Path
    content: dict


@dataclass
class PipPackageDownloadInfo:
    url: str

    def __init__(self, props):
        self.url = props["url"]


@dataclass
class PipPackageMetadata:
    name: str
    version: str

    def __init__(self, props):
        self.name = props["name"]
        self.version = props["version"]


@dataclass
class PipPackage:
    requested: bool
    download_info: PipPackageDownloadInfo
    metadata: PipPackageMetadata

    def __init__(self, props):
        self.requested = props["requested"]
        self.download_info = PipPackageDownloadInfo(props["download_info"])
        self.metadata = PipPackageMetadata(props["metadata"])

    @property
    def filename(self) -> str:
        url = urlparse(self.download_info.url)
        path = Path(url.path)
        return path.name

    @property
    def relative_wheel_path(self) -> str:
        return WHEEL_PATH.joinpath(self.filename).relative_to(APP_PATH).as_posix()


class PipTransaction:
    install: list[PipPackage]

    def __init__(self, props):
        self.install = [PipPackage(pkg) for pkg in props["install"]]


@dataclass
class FlaggedPackage:
    name: str
    is_direct: bool

    @property
    def reason(self) -> str:
        return WARN_WHEELS[self.name]


def load_app_json() -> AppJson:
    json_files = APP_PATH.glob("*.json")
    for json_file in json_files:
        try:
            with json_file.open("r") as fd:
                json_content = json.load(fd)
                if "appid" in json_content:
                    return AppJson(json_file, json_content)
        except (OSError, json.JSONDecodeError):
            print(f"Ignoring {json_file.name} as it cannot be loaded")

    raise ValueError("Cannot find a valid SOAR app JSON in current directory")


def prepare_wheels_directory():
    if WHEEL_PATH.exists():
        if WHEEL_PATH.is_dir():
            shutil.rmtree(WHEEL_PATH.absolute())
        else:
            raise RuntimeError(
                f"Wheel path ({WHEEL_PATH.absolute()}) exists but is not a directory. "
                "Please clean it up manually."
            )
    WHEEL_PATH.mkdir()
    print(f"Prepared wheel directory ({WHEEL_PATH.absolute()})")


def generate_pip_transaction() -> PipTransaction:
    try:
        pip_command = subprocess.run(
            [
                "pip",
                "install",
                "--quiet",
                "--ignore-installed",
                "--dry-run",
                "--report=-",
                f"--python-version={TARGET_PYTHON}",
                f"--platform={TARGET_PLATFORM}",
                "--only-binary=:all:",
                f"--requirement={REQUIREMENTS_PATH.absolute()}",
            ],
            capture_output=True,
            check=True,
        )
        return PipTransaction(json.loads(pip_command.stdout))
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        print(e.stderr.decode())
        raise RuntimeError(f"Failed to generate Pip transaction: pip returned exit code {e.returncode}")


def fetch_wheels(packages: list[PipPackage]):
    for package in packages:
        wheel_path = WHEEL_PATH.joinpath(package.filename)
        request = requests.get(package.download_info.url)
        request.raise_for_status()
        wheel_path.write_bytes(request.content)
        print(f"Downloaded {package.relative_wheel_path}")


def print_stanza_cleanup_notice(filename: str, stanza_name: str):
    print(
        f"::notice file={filename},line=1::Removed `{stanza_name}` from the JSON file, "
        "as it is no longer needed."
    )


def write_wheels_to_json(packages: list[PipPackage]):
    app_json = load_app_json()

    dependencies_key_regex = re.compile(r"^pip(\d+)_dependencies$")
    dict_keys = list(app_json.content.keys())
    for key in dict_keys:
        if dependencies_key_regex.fullmatch(key):
            print_stanza_cleanup_notice(app_json.path.name, key)
            del app_json.content[key]

    wheels = [
        {"module": package.metadata.name, "input_file": package.relative_wheel_path}
        for package in packages
    ]

    app_json.content["pip_dependencies"] = {"wheel": wheels}
    with app_json.path.open("w") as json_file:
        json.dump(app_json.content, json_file, indent=APP_JSON_INDENT)
    print(f"Saved dependencies to {app_json.path.name}")


def print_redundant_requirement_warning(package_name: str):
    print(
        f"::warning file=requirements.txt,line=1::`{package_name}` is provided by the SOAR platform. "
        "Its wheels will not be bundled into the repo. "
        "Consider removing it, or moving it to `requirements-dev.txt`."
    )


def print_flagged_package_warning(package_name: str, direct: bool):
    if direct:
        warning_preface = f"`{package_name}` is listed in `requirements.txt`."
    else:
        warning_preface = f"A requirement has `{package_name}` as a dependency."
    warning_reason = WARN_WHEELS.get(package_name)
    print(f"::warning file=requirements.txt,line=1::{warning_preface} {warning_reason}")


def put_summary_comment(redundant_packages: list[str], flagged_packages: list[FlaggedPackage]):
    if github_token := os.environ.get("GITHUB_TOKEN"):
        auth = Auth.Token(github_token)
        github = Github(auth=auth)
    else:
        print("Skipping summary comment because no GITHUB_TOKEN was set.")
        return
    
    if repo_name := os.environ.get("GITHUB_REPO"):
        repo = github.get_repo(repo_name)
        if ref_name := os.environ.get("GITHUB_REF"):
            ref = repo.get_commit(ref_name)
            pulls = ref.get_pulls()
        else:
            print("SKipping summary comment because no GITHUB_REF was set.")
            return
    else:
        print("Skipping summary comment because no GITHUB_REPO was set.")
        return
    
    if pulls.totalCount == 0:
        print("Skipping summary comment because there are no PRs associated with this commit.")
        return

    comment_lines: list[str] = []

    if redundant_packages:
        comment_lines.append("# :warning: Redundant packages")
        comment_lines.append("The following packages are provided by the SOAR platform, and do not need to be included with each connector. Their wheels will not be bundled into the repo.")
        comment_lines.append("Consider removing them from `requirements.txt`, or moving them to `dev-requirements.txt`.")
        for package in redundant_packages:
            comment_lines.append(f"- `${package}`")
        comment_lines.append("---")

    for package in flagged_packages:
        if package.is_direct:
            comment_lines.append(f"# :warning: `{package.name}` is listed in `requirements.txt`.")
        else:
            comment_lines.append(f"# :warning: A requirement has `{package.name}` as a dependency.")
        comment_lines.append(f"\n{package.reason}\n")
        comment_lines.append("---")

    if comment_lines:
        comment_body = '\n'.join(comment_lines)
        for pull in pulls:
            pull.create_issue_comment(comment_body)


def main():
    pip_transaction = generate_pip_transaction()

    wheels_to_fetch: list[PipPackage] = []

    redundant_packages: list[str] = []
    flagged_packages: list[FlaggedPackage] = []

    for dependency in pip_transaction.install:
        name = dependency.metadata.name
        direct = dependency.requested
        if name in IGNORED_WHEELS:
            print(f"Skipping {name} as it is provided by SOAR platform.")
            if direct:
                redundant_packages.append(name)
                print_redundant_requirement_warning(name)
        else:
            wheels_to_fetch.append(dependency)
            print(f"Will download {name}.")
            if name in WARN_WHEELS:
                print(f"Will recommend removing {name}.")
                flagged_packages.append(FlaggedPackage(name, direct))
                print_flagged_package_warning(name, direct)

    print(f"Will fetch: {[w.metadata.name for w in wheels_to_fetch]}")

    prepare_wheels_directory()
    fetch_wheels(wheels_to_fetch)
    write_wheels_to_json(wheels_to_fetch)

    put_summary_comment(redundant_packages, flagged_packages)


if __name__ == "__main__":
    main()
