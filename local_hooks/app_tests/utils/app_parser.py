import ast
import json
import os
import re

from packaging.version import Version

from .phantom_constants import APP_EXTS
from functools import cached_property
from pathlib import Path
from typing import Optional


class ParserError(Exception):
    pass


class AppParser:
    def __init__(self, local_repo_location: Path) -> None:
        self._app_code_dir = local_repo_location

    @cached_property
    def excludes(self):
        try:
            lines = (self._app_code_dir / "exclude_files.txt").read_text().splitlines()
            return set(line.strip() for line in lines)
        except OSError:
            return set()
        except Exception as e:
            raise ParserError(str(e)) from None

    @cached_property
    def min_phantom_version(self):
        return Version(self._get_from_json("min_phantom_version"))

    @cached_property
    def filepaths(self):
        # Gets all files in app source that are not hidden or excluded
        files = []
        safe_excludes = set(
            f for f in self.excludes if not any(f.endswith(ext) for ext in APP_EXTS)
        )

        for dirpath, _, file_lst in os.walk(self._app_code_dir):
            if not re.search(r"/\.", dirpath):
                for file in (f for f in file_lst if not (f in safe_excludes or f.startswith("."))):
                    files.append(os.path.realpath(os.path.join(dirpath, file)))
        return files

    @cached_property
    def filenames(self):
        return [os.path.basename(f) for f in self.filepaths]

    @cached_property
    def files(self):
        # Gets all files' contents in a dict
        files = {}
        for filepath in self.filepaths:
            try:
                with open(filepath, encoding="utf-8") as f:
                    files[filepath] = f.read()
            except UnicodeDecodeError:
                continue
        return files

    @property
    def app_json_name(self):
        # Get all json files in top level of app directory to send to finder function
        json_filenames = [
            fname for fname in os.listdir(self._app_code_dir) if fname.endswith(".json")
        ]

        try:
            return self.find_app_json_name(json_filenames)
        except Exception as e:
            raise ParserError(str(e)) from None

    def find_app_json_name(self, json_filenames):
        """
        Given a list of possible json files and the app repo name, return the name of the file
        that is most likely to be the app repo's main module json
        """
        # Multiple json files. Exclude known JSON filenames and expect only one at the end regardless of name.
        # Other places (e.g. Splunkbase) enforce a single top-level JSON file anyways.
        filtered_json_filenames = []
        for fname in json_filenames:
            # Ignore the postman collection JSON files
            if "postman_collection" in fname.lower():
                continue
            filtered_json_filenames.append(fname)

        if len(filtered_json_filenames) == 0:
            raise ValueError("No JSON file found in top level of app repo! Aborting tests...")

        if len(filtered_json_filenames) > 1:
            raise ValueError(
                f"Multiple JSON files found in top level of app repo: {filtered_json_filenames}."
                "Aborting because there should be exactly one top level JSON file."
            )

        # There's only one json file in the top level, so it must be the app's json
        return filtered_json_filenames[0]

    @property
    def _app_json_filepath(self) -> Path:
        sdk_app_path = self._app_code_dir / "sdk_app_manifest.json"
        if sdk_app_path.exists():
            return sdk_app_path

        return self._app_code_dir / self.app_json_name

    @cached_property
    def app_json(self):
        # Gets the loaded json, preserving key order
        try:
            json_content = json.loads(self._app_json_filepath.read_text())
            return json_content
        except FileNotFoundError as e:
            raise ParserError(f"File not found {self._app_json_filepath}") from e
        except json.JSONDecodeError as e:
            raise ParserError(f"JSON decoding failed for file: {self._app_json_filepath}") from e

    def update_app_json(self, app_json_content):
        app_json_str = json.dumps(app_json_content, indent=4)
        if not app_json_str.endswith("\n"):
            app_json_str += "\n"
        with open(self._app_json_filepath, "w") as f:
            f.write(app_json_str)
        self.refresh_app_json()

    @cached_property
    def all_calldefs(self):
        # Get all the calldefs of all funcdefs
        all_calldefs = []
        for funcdef in self.all_funcdefs:
            all_calldefs += self._get_calldefs(funcdef)
        return all_calldefs

    @cached_property
    def uv_lock_file(self) -> Optional[Path]:
        """
        Find uv.lock file in the connector_path or its subdirectories.
        Returns the path to the uv.lock file if found, None otherwise.
        """
        # Check top level directory first
        uv_lock_path = self._app_code_dir / "uv.lock"
        if uv_lock_path.exists():
            return uv_lock_path

        # Check subdirectories
        for uv_lock_path in self._app_code_dir.rglob("uv.lock"):
            return uv_lock_path

        return None

    @cached_property
    def connector_filepath(self):
        # Find the connector filename
        try:
            connector_filename = self._get_from_json("main_module").rstrip("c")
        except AttributeError:
            raise ParserError(
                "main_module in app json is of type {}, but should be a string".format(
                    type(self.app_json["main_module"])
                )
            ) from None

        if not connector_filename.endswith(".py"):
            # sdkfied app
            if uv_lock_path := self.uv_lock_file:
                path_to_main_module = connector_filename.split(":")[0]
                full_path = "/".join(path_to_main_module.split("."))
                full_path += ".py"
                return uv_lock_path.parent / full_path

        if connector_filename in self.filenames:
            return os.path.join(self._app_code_dir, connector_filename)

        raise ParserError(
            f'Expected to find connector file "{connector_filename}", but was not found in {self._app_code_dir}'
        )

    def _get_from_json(self, key):
        try:
            return self.app_json[key]
        except KeyError:
            raise ParserError(f"'{key}' key not found in app json. Aborting execution") from None

    def _get_tree(self, filepath):
        # Gets the ast tree
        if not filepath:
            raise ParserError(f"Cannot get ast tree of empty filepath: {filepath}")
        try:
            if os.path.exists(filepath):
                with open(filepath) as f:
                    return ast.parse(f.read())
            else:
                return ast.parse(filepath)
        except OSError:
            raise ParserError(f"Could not open file at {filepath}") from None

    def _get_classdefs(self, tree):
        # Gets classdefs from a tree
        if not tree:
            raise ParserError(f"Cannot get classdefs of empty tree: {tree}")
        return [node for node in tree.body if isinstance(node, ast.ClassDef)]

    @cached_property
    def all_funcdefs(self):
        # Gets all the funcdefs of all classdefs
        classdefs = self._get_classdefs(self._get_tree(self.connector_filepath))
        all_funcdefs = []
        for classdef in classdefs:
            all_funcdefs += self._get_funcdefs(classdef)
        return all_funcdefs

    def _get_funcdefs(self, classdef):
        # Gets funcdefs from a classdef
        if not classdef:
            raise ParserError(f"Cannot get funcdefs of empty classdef: {classdef}")
        return [node for node in classdef.body if isinstance(node, ast.FunctionDef)]

    def _get_calldefs(self, funcdef):
        # Gets all funcs called from a method, including ones nested far inside
        if not funcdef:
            raise ParserError(f"Cannot get calldefs of empty funcdef: {funcdef}")
        return [node for node in ast.walk(funcdef) if isinstance(node, ast.Call)]

    def get_id_attr(self, node):
        # Name = node.id in 'name'; Name = node.attr in 'class.name'
        arguments = set()
        if isinstance(node, ast.Name):
            arguments.add(node.id)
        elif isinstance(node, ast.Attribute):
            arguments.add(node.attr)
        elif isinstance(node, ast.JoinedStr):
            # this checks for f-strings
            for value in node.values:
                if isinstance(value, ast.FormattedValue) and isinstance(value.value, ast.Name):
                    arguments.add(value.value.id)

        return arguments

    def refresh_app_json(self):
        self.__dict__.pop("app_json", None)
