import json
import logging
import os
from pathlib import Path


def get_app_json(app_json_dir):
    logging.info("Looking for app JSON in: %s", app_json_dir)
    app_json_name = [f for f in os.listdir(app_json_dir)
                     if f.endswith(".json")
                     and "postman_collection" not in f][0]
    json_file_path = Path(app_json_dir, app_json_name)
    logging.info("Loading json: %s", app_json_name)
    with open(json_file_path, "r") as json_file:
        return json.load(json_file)

