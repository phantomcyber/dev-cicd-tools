from app_tests.test_suite import TestSuite
import json
import textwrap
from typing import Any
from jsonschema import exceptions
from jsonschema.validators import Draft202012Validator as JsonSchemaValidator
from app_tests.utils import create_test_result_response
from app_tests.utils.phantom_constants import (
    SPLUNK_SUPPORTED,
    TEST_PASS_MESSAGE,
    CURRENT_MIN_PHANTOM_VERSION,
    APPID_TO_NAME_FILEPATH,
    APPID_TO_PACKAGE_NAME_FILEPATH,
    MINIMAL_DATA_PATHS,
    PASSWORD_KEYS,
)
from operator import itemgetter
import traceback
from distutils.version import LooseVersion
from pathlib import Path


class JSONTests(TestSuite):
    def __init__(self, app_repo_name, repo_location, **kwargs):
        super().__init__(app_repo_name, repo_location, **kwargs)
        self._app_json = self._parser.app_json

        self._app_is_certified = self._parser.app_json["publisher"] == "Splunk"

    @staticmethod
    def format_as_index(indices: list[Any], container: str = "schema") -> str:
        """
        Largely copied from jsonschema source:
        Construct a single string containing indexing operations for the indices.

        For example for a container ``bar``, [1, 2, "foo"] -> bar[1][2]["foo"]

        Arguments:

            container (str):

                A word to use for the thing being indexed

            indices (sequence):

                The indices to format.

        """
        if not indices:
            return container
        return f"{container}[{']['.join(repr(index) for index in indices)}]"

    @TestSuite.test
    def validate_json_schema(self):
        """
        Validates the structure of the app json
        """
        APP_TESTS_DIR = Path(__file__).parent.resolve()
        schema_path = APP_TESTS_DIR / "app_schema.json"
        verbose = []
        message = TEST_PASS_MESSAGE

        with open(schema_path) as app_schema_file:
            app_schema = json.load(app_schema_file)

        validator = JsonSchemaValidator(app_schema)
        for err in sorted(validator.iter_errors(self._app_json), key=exceptions.relevance):
            msg = textwrap.dedent(
                f"""
                * Failed validating {err.validator!r} at {JSONTests.format_as_index(err.schema_path, "schema")}
                On {JSONTests.format_as_index(err.path, "instance") or "root"}
                {err.message}
                """
            )
            verbose.append(textwrap.indent(msg, "    "))

        return create_test_result_response(
            success=not verbose,
            message=message if not verbose else "Failed app json schema validation",
            verbose=verbose,
        )

    @TestSuite.test(remove_tags=[SPLUNK_SUPPORTED])
    def check_communitiy_publisher(self):
        """
        Verifies the value of 'publisher' in the app JSON for developer supported apps.
        """
        if self._app_json.get("publisher") == "Splunk":
            failure_message = "Publisher in app JSON should be 'Splunk Community' or third party."
            return create_test_result_response(success=False, message=failure_message)

        return create_test_result_response(success=True)

    @TestSuite.test
    def check_sequential_order(self):
        """
        Checks whether order of configuration parameters, action parameters, and action output columns
        are sequential and zero-indexed
        """

        def check_sequence(order_tuples):
            try:
                order_tuples = ((a, int(b)) for a, b in order_tuples)
                return all(
                    order == i
                    for i, (_, order) in enumerate(sorted(order_tuples, key=itemgetter(1)))
                )
            except Exception:
                traceback.print_exc()
                return False

        nonsequential_items = []

        # Check order for app config parameters
        config_order = [
            (config_param, config_fields.get("order", -1))
            for config_param, config_fields in self._app_json["configuration"].items()
        ]
        if not check_sequence(config_order):
            nonsequential_items.append("app configuration parameters")

        for action in self._app_json["actions"]:
            # Ignore on poll action for sequential ordering test
            if action["action"] == "on poll":
                continue

            # Check order for action parameters
            action_order = [
                (param, param_fields.get("order", -1))
                for param, param_fields in action["parameters"].items()
            ]
            if not check_sequence(action_order):
                nonsequential_items.append("action parameters for `{}`".format(action["action"]))

            # Check order for action outputs
            # Not every output will have column_order
            output_order = [
                (output_obj["data_path"], output_obj["column_order"])
                for output_obj in action["output"]
                if "column_order" in output_obj
            ]
            if not check_sequence(output_order):
                nonsequential_items.append(
                    "action output parameters for `{}`".format(action["action"])
                )

        correct_order = len(nonsequential_items) == 0
        failure_mesage = "Configuration parameter(s), action parameter(s), and/or action output(s) are not sequential or do not start at zero."
        verbose = [
            f"Ordering of {item} are not sequential or do not start at zero"
            for item in nonsequential_items
        ]

        return create_test_result_response(
            success=correct_order,
            message=TEST_PASS_MESSAGE if correct_order else failure_mesage,
            verbose=verbose,
        )

    @TestSuite.test(tags=["pre-release"])
    def check_main_module(self):
        """
        Verifies that the main module field of the json is a valid connector filename
        """
        app_json = self._app_json
        verbose = []
        main_module = app_json["main_module"]

        # Either way, the file needs to exist in the app
        if main_module.replace(".pyc", ".py") not in (
            f.replace(".pyc", ".py") for f in self._parser.filenames
        ):
            verbose.append(
                '"main_module" file from json ({}) not found in list of app files. Files found: {}'.format(
                    main_module, ", ".join(self._parser.filenames)
                )
            )

        return {
            "success": not verbose,
            "message": TEST_PASS_MESSAGE
            if not verbose
            else 'The "main_module" field of the app json is missing or incorrect',
            "verbose": verbose,
        }

    @TestSuite.test(critical=False)
    def check_min_platform_version(self):
        """
        Checks that if pip packages are installed, phantom version > CURRENT_MIN_PHANTOM_VERSION
        """
        msg = TEST_PASS_MESSAGE
        min_version = LooseVersion(self._app_json["min_phantom_version"])
        if min_version < LooseVersion(CURRENT_MIN_PHANTOM_VERSION):
            msg = f'Min Phantom version in app json is too low. Found: "{min_version}" but expected >= "{CURRENT_MIN_PHANTOM_VERSION}". Modifying {self._parser.app_json_name}'
            # As apart of the CI migration we are not updating the min_phantom_version because it is considered a chore task so the following code is commented out
            # self._app_json["min_phantom_version"] = CURRENT_MIN_PHANTOM_VERSION
            # self._parser.update_app_json(self._app_json)
        return create_test_result_response(
            success=msg == TEST_PASS_MESSAGE, message=msg, fixed=True
        )

    @TestSuite.test(critical=False)
    def check_test_connectivity(self):
        """
        Checks whether test_connectivity has progress message if it exists
        """
        message = TEST_PASS_MESSAGE

        if not self._has_test_connectivity():
            message = "Test connectivity not found in JSON"

        return create_test_result_response(success=message == TEST_PASS_MESSAGE, message=message)

    def _has_test_connectivity(self):
        for action in self._parser.app_json["actions"]:
            if action["action"] == "test connectivity":
                return True
        return False

    @TestSuite.test
    def check_valid_app_name_and_guid(self):
        """
        App Name and GUID must be unique, and GUID must be a lowercased string
        """
        app_name = self._app_json["name"]
        app_guid = self._app_json["appid"].lower()

        with open(APPID_TO_NAME_FILEPATH) as file:
            app_guid_to_name = json.loads(file.read())
            if app_guid_to_name.get(app_guid) == app_name:
                return create_test_result_response(success=True, message=TEST_PASS_MESSAGE)

            message = ""
            if app_guid in app_guid_to_name:
                message = f"Invalid GUID for app `{app_name}`: GUID `{app_guid}` already maps to app `{app_guid_to_name.get(app_guid)}`"
            elif app_name in app_guid_to_name.values():
                existing_guid = next(
                    guid for guid, name in app_guid_to_name.items() if name == app_name
                )
                message = f"Invalid GUID in json for app `{app_name}`: Existing GUID `{existing_guid}` does not match GUID in json `{app_guid}`"
            else:
                message = f"GUID and app not listed in {APPID_TO_NAME_FILEPATH}"

        return create_test_result_response(
            success=not message, message=TEST_PASS_MESSAGE if not message else message
        )

    @TestSuite.test(tags=["pre-release"])
    def check_app_package_name(self):
        """
        Package name is unique
        """
        package_name = self._app_json["package_name"]
        app_guid = self._app_json["appid"]

        with open(APPID_TO_PACKAGE_NAME_FILEPATH) as file:
            package_name_map = json.loads(file.read())
            if package_name_map.get(app_guid) == package_name:
                return create_test_result_response(success=True, message=TEST_PASS_MESSAGE)

            message = ""
            if app_guid in package_name_map:
                message = f"Invalid GUID for package `{package_name}`: GUID `{app_guid}` already maps to package `{package_name_map.get(app_guid)}`"
            elif package_name in package_name_map.values():
                existing_guid = next(
                    guid for guid, name in package_name_map.items() if name == package_name
                )
                message = f"Invalid GUID in json for package `{package_name}`: Existing GUID `{existing_guid}` does not match GUID in json `{app_guid}`"
            else:
                message = (
                    f"GUID and app package name not listed in {APPID_TO_PACKAGE_NAME_FILEPATH}"
                )

        return create_test_result_response(
            success=not message, message=TEST_PASS_MESSAGE if not message else message
        )

    @TestSuite.test
    def check_action_param_prefixes(self):
        """
        Every parameter has an action_result.parameter associated with it
        """
        app_json_actions = self._app_json.get("actions")

        message = TEST_PASS_MESSAGE
        verbose = []
        for index, action in enumerate(app_json_actions):
            if action["action"] in ("test connectivity", "on poll"):
                continue
            action_parameters = action.get("parameters", {})  # Gets the parameters, if any
            if not action_parameters:
                continue

            action_output = self._get_data_paths(action, parameters=True)
            action_output_path_values = set(action_output.keys())

            for param_name in action_parameters:
                formatted_param = f"action_result.parameter.{param_name}"
                if formatted_param not in action_output_path_values:
                    # if this check fails that means the validate_json_schema test will also fail which is why it's fine to do this
                    if "data_type" in action_parameters[param_name]:
                        new_output_param = {
                            "data_path": formatted_param,
                            "data_type": action_parameters[param_name]["data_type"],
                        }
                        self._app_json["actions"][index]["output"].append(new_output_param)
                        verbose.append(f"Missing action result output for {formatted_param}")

            parameters_formatted = set(
                f"action_result.parameter.{name}" for name in action_parameters
            )
            action_output_to_remove = []
            for data_path, idx_param in action_output.items():
                if data_path not in parameters_formatted:
                    action_output_to_remove.append(idx_param)
                    verbose.append(f"Extra action result output for {data_path}")

            for idx_param in reversed(action_output_to_remove):
                self._app_json["actions"][index]["output"].pop(idx_param)

        if verbose:
            message = f"Action results should only contain an action_result.parameter key for every action parameter. Modifying {self._parser.app_json_name}"
            self._parser.update_app_json(self._app_json)

        return create_test_result_response(
            success=not verbose, message=message, verbose=verbose, fixed=True
        )

    @TestSuite.test
    def check_action_param_matching_contains(self):
        """
        Every parameter for an action with contains has an action_result.parameter with the same contains
        """
        action_list = [act for act in self._app_json["actions"]]
        verbose = []
        for index, action in enumerate(action_list):
            if action["action"] in ("test connectivity", "on poll"):
                continue
            action_output = self._get_data_paths(action, parameters=True)
            param_contains = {
                param: config["contains"]
                for param, config in action["parameters"].items()
                if config.get("contains")
            }

            for param, contain in param_contains.items():
                action_res_param = f"action_result.parameter.{param}"
                if action_output.get(action_res_param):
                    data_path_contains = self._get_output_param_value(
                        index, action_output[action_res_param], "contains"
                    )
                    if contain != data_path_contains:
                        self._update_action_output(
                            index, action_output[action_res_param], "contains", contain
                        )
                        action_name = action["action"]
                        verbose.append(
                            f"Action '{action_name}': parameter '{param}' contains value must match output of {contain}"
                        )

        msg = TEST_PASS_MESSAGE
        if verbose:
            self._parser.update_app_json(self._app_json)
            msg = f"Action parameter contains should match those belonging to its related action_result.parameter contains. Modifying {self._parser.app_json_name}"

        return create_test_result_response(
            success=not verbose, message=msg, verbose=verbose, fixed=True
        )

    @TestSuite.test
    def check_minimal_data_paths(self):
        """
        Checks to make sure each action includes the minimal required data paths
        """
        app_json_actions = [act for act in self._app_json["actions"]]
        verbose = []
        message = TEST_PASS_MESSAGE
        for idx, action in enumerate(app_json_actions):
            if action["action"] in ("test connectivity", "on poll"):
                continue
            data_paths = set(
                [
                    (path, data_path_dic["data_type"])
                    for path, data_path_dic in self._get_data_paths(action).items()
                ]
            )
            for minimal_path in MINIMAL_DATA_PATHS - data_paths:
                data_path, data_type = minimal_path
                self._app_json["actions"][idx]["output"].append(
                    {"data_path": data_path, "data_type": data_type}
                )
                action_name = action["action"]
                verbose.append(f"{action_name} missing {data_path}")

        if verbose:
            self._parser.update_app_json(self._app_json)
            message = f"One or more actions are missing a required data paths. Modifying {self._parser.app_json_name}. Please ensure these paths are set in their respective actions"

        return create_test_result_response(
            success=not verbose,
            message=message,
            verbose=verbose,
        )

    def _get_data_paths(self, action, parameters=False):
        """
        Retrieves the action output from the action.

        :param action: Dict of the action as defined in the json
        :param parameters: True if retrieving action_result.parameters only, False otherwise.  Mutually-exclusive with
                           contains.
        :param contains: True if retrieving the contains of data_paths only, False otherwise.  Mutually-exclusive with
                         parameters.

        :returns: List of data paths, or list of all parameter data_paths if parameters, or dict of data_paths and contains
                  if contains.
        """

        action_outputs = {}

        action_output_raw = action.get("output", [])

        for index, data_path in enumerate(action_output_raw):
            data_path_value = data_path.get("data_path")
            if data_path_value:
                if parameters:
                    if data_path_value.startswith("action_result.parameter"):
                        action_outputs[data_path_value] = index
                else:
                    action_outputs[data_path_value] = data_path

        return action_outputs

    def _get_output_param_value(self, action: int, idx: int, key: str) -> Any:
        """Gets the value of a certain key in the actions output

        Args:
            action (int): Index of the action in the actions list
            idx (int): Element in an actions output being updated
            key (string): Specific key being updated
        """
        return self._app_json["actions"][action]["output"][idx].get(key)

    def _update_action_output(self, action: int, idx: int, key: str, value: Any) -> None:
        """Updates an actions output for the given key

        Args:
            action (int): Index of the action in the actions list
            idx (int): Element in an actions output being updated
            key (string): Specific key being updated
            value (any): New value of the key
        """
        self._app_json["actions"][action]["output"][idx][key] = value

    @TestSuite.test(critical=False)
    def fields_should_be_passwords(self):
        """
        Fields that look like passwords should be passwords
        """
        verbose = []

        for param_key in self._app_json.get("configuration", {}):
            param_options = self._app_json["configuration"][param_key]
            is_pswd = param_options.get("data_type") == "password"
            should_be_pswd = not is_pswd and any(key in param_key for key in PASSWORD_KEYS)

            if should_be_pswd:
                verbose.append(
                    f"JSON config param `{param_key}` should probably be of data_type `password`"
                )

        msg = (
            TEST_PASS_MESSAGE
            if not verbose
            else "Some configuration parameters may be secrets and should have password data types. Please review"
        )
        return create_test_result_response(success=not verbose, message=msg, verbose=verbose)
