import sys
import logging
from venv import logger
# sys.path.insert(1, "github-actions/start-release")
# import build_docs.py


def check_readme():
    pass

def main():
    logger.info("readme-check runs")

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("GENRATING README")
    sys.exit(main())
