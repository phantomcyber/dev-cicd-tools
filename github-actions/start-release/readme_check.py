#!/usr/bin/env python3
import argparse
import sys
import logging
from build_docs import main
from pathlib import Path


def validate_dir_path(path):
    if not Path(path).is_dir():
        raise argparse.ArgumentTypeError(f"Provided value: {path} is not a directory.")
    return path

def pass_args():
    default_path = Path().resolve()
    logging.info(" PATH CWD DEFAULT %s", default_path)
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--connector_path", default=default_path, type=validate_dir_path)
    parser.add_argument("--from_html", default=False, type=bool)
    args = parser.parse_args()
    logging.info(" ARGS %s", args)
    logging.info(" ARGS CONNECTOR PATH %s", args.connector_path)
    logging.info(" ARGS FROM HTML %s", args.from_html)
    logging.info(" PATH CWD %s", Path.cwd())
    logging.info(" PATH CWD DEFAULT %s", default_path)
    logging.info(" PATH FROM ARGS %s", args.connector_path)
    logging.info(" ARGS %s", sys.argv)
    return args

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(pass_args()))

