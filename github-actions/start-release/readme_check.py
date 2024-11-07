#!/usr/bin/env python3
import argparse
import sys
import logging
from build_docs import main
from pathlib import Path

# def main():
#     logger.info("readme-check runs")
#     build_docs(connector_path=Path.cwd(), app_version=None)

def pass_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("connector_path", default=Path.cwd())
    parser.add_argument("from_html", default=False)
    return parser.parse_args()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(pass_args()))

