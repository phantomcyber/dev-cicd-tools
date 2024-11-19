#!/usr/bin/env python3
import argparse
import sys
import logging
from build_docs import main as build_docs
from pathlib import Path


def validate_dir_path(path):
    if not Path(path).is_dir():
        raise argparse.ArgumentTypeError(f"{path} is not a directory.")
    return path

def pass_args():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--connector_path", default=Path.cwd(), type=validate_dir_path)
    parser.add_argument("--from_html", default=False, type=bool, nargs="?")
    parser.add_argument("--json_name", default=None, type=str, nargs="?")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(build_docs(pass_args()))

