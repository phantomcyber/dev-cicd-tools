import json
import subprocess
import sys
from pathlib import Path

import pytest

from local_hooks import generate_notice


def license_rows(*names: str) -> str:
    return json.dumps(
        [
            {
                "Name": name,
                "License": "MIT",
                "LicenseText": "Permission granted.",
                "NoticeText": "UNKNOWN",
                "URL": f"https://example.test/{name}",
                "Version": "1.0.0",
            }
            for name in names
        ]
    )


def completed(command: list[str], stdout: str = "", returncode: int = 0):
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "git+https://github.com/phantomcyber/convert-outlook-msg-file.git@0.1.0 "
            "#outlookmsgfile=0.1.0",
            "outlookmsgfile",
        ),
        (
            "outlookmsgfile @ "
            "git+https://github.com/phantomcyber/convert-outlook-msg-file.git@0.1.0",
            "outlookmsgfile",
        ),
        (
            "git+https://github.com/example/project.git@1.0#egg=Example_Project",
            "example-project",
        ),
        ("lxml==5.4.0", "lxml"),
        ("Requests>=2.32 # runtime HTTP client", "requests"),
        ("", None),
        ("# comment", None),
    ],
)
def test_get_requirement_name(line: str, expected):
    assert generate_notice.get_requirement_name(line) == expected


def test_get_package_dependencies_allows_missing_requirements(tmp_path: Path):
    assert generate_notice.get_package_dependencies(tmp_path / "requirements.txt") == []


def test_get_python_license_info_prefers_uvx(monkeypatch, tmp_path: Path):
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("demo-package==1.0.0\n")
    commands = []

    monkeypatch.setattr(
        generate_notice.shutil,
        "which",
        lambda command: "/usr/bin/uvx" if command == "uvx" else None,
    )

    def fake_run(command: list[str]):
        commands.append(command)
        return completed(command, license_rows("demo-package"))

    monkeypatch.setattr(generate_notice, "run_command", fake_run)

    rows = list(generate_notice.get_python_license_info(["demo-package"], requirements_path))

    assert [row.package_name for row in rows] == ["demo-package"]
    assert commands == [
        [
            "uvx",
            "--with-requirements",
            str(requirements_path),
            "pip-licenses",
            "--format=json",
            "--with-license-file",
            "--no-license-path",
            "--with-urls",
            "--with-notice-file",
            "--packages",
            "demo-package",
        ]
    ]


def test_get_python_license_info_can_use_uv_tool_run(monkeypatch, tmp_path: Path):
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("demo-package==1.0.0\n")
    commands = []

    monkeypatch.setattr(
        generate_notice.shutil,
        "which",
        lambda command: "/usr/bin/uv" if command == "uv" else None,
    )

    def fake_run(command: list[str]):
        commands.append(command)
        return completed(command, license_rows("demo-package"))

    monkeypatch.setattr(generate_notice, "run_command", fake_run)

    rows = list(generate_notice.get_python_license_info(["demo-package"], requirements_path))

    assert [row.package_name for row in rows] == ["demo-package"]
    assert commands[0][:4] == ["uv", "tool", "run", "--with-requirements"]


def test_get_python_license_info_falls_back_to_current_python_pip(monkeypatch, tmp_path: Path):
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("demo-package==1.0.0\n")
    commands = []

    monkeypatch.setattr(generate_notice.shutil, "which", lambda command: None)

    def fake_run(command: list[str]):
        commands.append(command)
        if command == [sys.executable, "-m", "pip", "--version"]:
            return completed(command, "pip 1.0\n")
        if command[:4] == [sys.executable, "-m", "pip", "install"]:
            return completed(command)
        if command[:3] == [sys.executable, "-m", "piplicenses"]:
            return completed(command, license_rows("demo-package"))
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(generate_notice, "run_command", fake_run)

    rows = list(generate_notice.get_python_license_info(["demo-package"], requirements_path))

    assert [row.package_name for row in rows] == ["demo-package"]
    assert commands == [
        [sys.executable, "-m", "pip", "--version"],
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "pip-licenses",
            "-r",
            str(requirements_path),
        ],
        [
            sys.executable,
            "-m",
            "piplicenses",
            "--format=json",
            "--with-license-file",
            "--no-license-path",
            "--with-urls",
            "--with-notice-file",
            "--packages",
            "demo-package",
        ],
    ]


def test_get_python_license_info_fails_without_uv_or_pip(monkeypatch, tmp_path: Path):
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("demo-package==1.0.0\n")

    monkeypatch.setattr(generate_notice.shutil, "which", lambda command: None)
    monkeypatch.setattr(
        generate_notice,
        "run_command",
        lambda command: completed(command, returncode=1),
    )

    with pytest.raises(RuntimeError, match="pip is not importable"):
        list(generate_notice.get_python_license_info(["demo-package"], requirements_path))


def test_get_python_license_info_fails_when_license_rows_are_missing(monkeypatch, tmp_path: Path):
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("demo-package==1.0.0\n")

    monkeypatch.setattr(
        generate_notice.shutil,
        "which",
        lambda command: "/usr/bin/uvx" if command == "uvx" else None,
    )
    monkeypatch.setattr(
        generate_notice,
        "run_command",
        lambda command: completed(command, "[]"),
    )

    with pytest.raises(RuntimeError, match="demo-package"):
        list(generate_notice.get_python_license_info(["demo-package"], requirements_path))
