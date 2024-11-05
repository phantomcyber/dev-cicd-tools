#!/usr/bin/env python3

import sys
import logging
from venv import logger
from build_docs import build_docs
from pathlib import Path

def main():
    logger.info("readme-check runs")
    build_docs(connector_path=Path.cwd(), app_version=None)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main())
