#!/usr/bin/env python3

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

MODERN_LINT_CONFIG_FILE = "pyproject.toml"
SEMGREP_RULES_DIR = "semgrep"


def copy_configs(dest_dir):
    """Override configurations for hooks"""
    dev_tools_dir = SCRIPT_DIR.parent
    lint_configs_dir = dev_tools_dir / "lint-configs"

    try:
        # Copy lint configs
        shutil.copyfile(
            lint_configs_dir / MODERN_LINT_CONFIG_FILE, dest_dir / MODERN_LINT_CONFIG_FILE
        )

        # Copy semgrep rules
        source_rules_dir = dev_tools_dir / SEMGREP_RULES_DIR
        dest_rules_dir = dest_dir / SEMGREP_RULES_DIR

        if source_rules_dir.exists():
            # Remove existing rules directory to ensure clean copy
            if dest_rules_dir.exists():
                shutil.rmtree(dest_rules_dir, ignore_errors=True)

            # Copy all files from source to destination
            shutil.copytree(source_rules_dir, dest_rules_dir)

        # Copy pre-commit directory
        source_precommit_dir = dev_tools_dir / "pre-commit"
        dest_precommit_dir = dest_dir / "pre-commit"

        if source_precommit_dir.exists():
            # Remove existing pre-commit directory to ensure clean copy
            if dest_precommit_dir.exists():
                shutil.rmtree(dest_precommit_dir, ignore_errors=True)

            # Copy all files from source to destination
            shutil.copytree(source_precommit_dir, dest_precommit_dir)

    except Exception:
        # We can safely ignore these errors since the files are already there
        pass


def main():
    copy_configs(Path.cwd())
    return 0


if __name__ == "__main__":
    sys.exit(main())
