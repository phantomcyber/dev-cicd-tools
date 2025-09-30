import logging
from pathlib import Path
from typing import Optional
import subprocess
import tempfile
import json
import shutil
import os


def ensure_uv_available():
    """
    Check if uv is installed and install it if not.
    Mimics the GitHub pipeline approach:
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    """
    # Check if uv is already available
    if shutil.which("uv"):
        logging.info("uv is already installed and available")
        return

    logging.info("uv not found, installing")

    try:
        # Download and execute the uv installer (equivalent to: curl -LsSf https://astral.sh/uv/install.sh | sh)
        logging.info("Downloading uv installer...")
        result = subprocess.run(
            ["curl", "-LsSf", "https://astral.sh/uv/install.sh"],
            capture_output=True,
            text=True,
            check=True,
        )

        logging.info("Executing uv installer...")
        subprocess.run(["sh"], input=result.stdout, text=True, check=True)

        # Add ~/.cargo/bin to PATH for current session (equivalent to: echo "$HOME/.cargo/bin" >> $GITHUB_PATH)
        cargo_bin = os.path.expanduser("~/.cargo/bin")
        current_path = os.environ.get("PATH", "")
        if cargo_bin not in current_path:
            os.environ["PATH"] = f"{cargo_bin}:{current_path}"
            logging.info("Added %s to PATH", cargo_bin)

    except subprocess.CalledProcessError as e:
        logging.error("Failed to install uv: %s", e)
        raise RuntimeError(f"uv installation failed: {e}")


def find_uv_lock_file(connector_path: Path) -> Optional[Path]:
    """
    Find uv.lock file in the connector_path or its subdirectories.
    Returns the path to the uv.lock file if found, None otherwise.
    """
    # By convention, SDK apps are managed by uv and old apps are not
    for uv_lock_path in connector_path.rglob("uv.lock"):
        logging.info("Found uv.lock at: %s", uv_lock_path)
        return uv_lock_path


def load_sdk_apps_enviornment(uv_lock_dir: Path):
    """
    Load the SDK app's environment.
    """
    ensure_uv_available()

    pyproject_path = uv_lock_dir / "pyproject.toml"
    if pyproject_path.exists():
        logging.info("Installing dependencies from pyproject.toml")
        try:
            subprocess.run(
                ["uv", "sync"], cwd=uv_lock_dir, check=True, capture_output=True, text=True
            )
            logging.info("Successfully installed dependencies")

        except subprocess.CalledProcessError as e:
            logging.error("Failed to install dependencies: %s", e)
            raise e
    else:
        raise ValueError("No pyproject.toml found in %s", uv_lock_dir)


def generate_sdk_app_manifest(uv_lock_dir: Path) -> dict:
    ensure_uv_available()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_manifest_path = Path(temp_dir) / "sdk_app_manifest.json"
        try:
            # Use uv run to execute soarapps in the SDK app's environment
            subprocess.run(
                [
                    "uv",
                    "run",
                    "soarapps",
                    "manifests",
                    "create",
                    str(temp_manifest_path),
                    ".",
                ],
                check=True,
                cwd=uv_lock_dir,  # Run from the SDK app directory
            )
            logging.info("Successfully generated SDK manifest in temp directory")

            with open(temp_manifest_path) as f:
                return json.load(f)

        except subprocess.CalledProcessError as e:
            logging.error("Failed to generate SDK manifest: %s", e)
            raise e
