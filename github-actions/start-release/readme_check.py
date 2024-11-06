#!/usr/bin/env python3
import argparse
import sys
import logging
from venv import logger
from build_docs import main
from pathlib import Path

# def main():
#     logger.info("readme-check runs")
#     build_docs(connector_path=Path.cwd(), app_version=None)
#
def pass_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("connector_path", help="Path to the connector", default=Path.cwd())
    parser.add_argument("from_html", nargs='?', default=False, help="Build from html instead of md")
    return parser.parse_args()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(pass_args()))

