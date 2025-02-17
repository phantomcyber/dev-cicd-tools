#!/usr/bin/env python3
import yaml
import os
from pathlib import Path
from copy_configs import copy_configs


def main():
    # Copy configuration files first
    copy_configs(Path(os.getcwd()))

    # Get central hooks template
    central_hooks_path = os.path.join(os.path.dirname(__file__), "pre-commit-hooks-template.yaml")
    with open(central_hooks_path) as f:
        central_hooks = yaml.safe_load(f)

    # Write to the connector's pre-commit config for running hooks
    config_path = ".pre-commit-config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(central_hooks, f)


if __name__ == "__main__":
    main()
