import logging
import os
import re
import json
import sys
from pathlib import Path


def get_app_json(app_json_dir, json_name):
    logging.info("Looking for app JSON in: %s", app_json_dir)
    if not json_name:
        try:
            app_json_name = next(
                f
                for f in os.listdir(app_json_dir)
                if f.endswith(".json") and "postman_collection" not in f
            )
        except IndexError:
            logging.error("Unable to find app JSON")
            sys.exit(1)
    else:
        if os.path.isfile(os.path.join(app_json_dir, json_name)):
            app_json_name = json_name
        else:
            logging.error("Provided JSON name does not exist")
            sys.exit(1)

    json_file_path = Path(app_json_dir, app_json_name)
    logging.info("Loading json: %s", app_json_name)
    with open(json_file_path) as json_file:
        return json.load(json_file)


def generate_gh_fragment(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text)
    return re.sub(r"[\s]", "-", text)
