#!/usr/bin/env python3
import argparse
import logging
from typing import Union
from build_docs import BuildDocsArgs, main as build_docs
from pathlib import Path


def validate_dir_path(path: Union[str, Path]) -> Path:
    path = Path(path)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{path} is not a directory.")
    return path


def pass_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--connector-path", default=Path.cwd(), type=validate_dir_path)
    parser.add_argument("--from-html", action="store_true")
    parser.add_argument("--json-name")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    build_docs(BuildDocsArgs(**vars(pass_args())))
