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
    default_path = str(Path.cwd())
    parser = argparse.ArgumentParser()
    parser.add_argument("connector_path", default=lambda:default_path)
    parser.add_argument("from_html", default=False)
    args =  parser.parse_args()
    logging.info(" ARGS %s", args)
    logging.info(" ARGS CONNECTOR PATH %s", args.connector_path)
    logging.info(" ARGS FROM HTML %s", args.from_html)
    logging.info(" PATH CWD %s", Path.cwd())
    logging.info(" PATH CWD DEFAULT %s", default_path)
    return args

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(pass_args()))

