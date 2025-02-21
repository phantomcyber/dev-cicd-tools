from test_suite import TestSuite
import json
import jsonschema
from jsonschema import validate
from utils import create_test_result_response
from utils.phantom_constants import (
    SPLUNK_SUPPORTED,
    DEVELOPER_SUPPORTED,
    TEST_PASS_MESSAGE,
    CURRENT_MIN_PHANTOM_VERSION,
    APPID_TO_NAME_FILEPATH,
    APPID_TO_PACKAGE_NAME_FILEPATH,
    MINIMAL_DATA_PATHS,
    PASSWORD_KEYS
)
from operator import itemgetter
import traceback
from distutils.version import LooseVersion

class JSONTests(TestSuite):
    def __init__(self, app_repo_name, repo_location, **kwargs):
        super().__init__(app_repo_name, repo_location, **kwargs)
        self._app_json = self._parser.app_json

        self._app_is_certified = self._parser.app_json["publisher"] == "Splunk"
    
    @TestSuite.test
    def validate_json_schema(self):
        with open("app_schema.json") as app_schema_file:
            app_schema = json.load(app_schema_file)
        
        try:
           validate(instance=self._app_json, schema=app_schema) 
           return create_test_result_response(success=True, message="Successfully validated app json against schema")
        except jsonschema.exceptions.ValidationError as e:
            return create_test_result_response(success=False, message=e.message)
    
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

        return create_test_result_response(success=correct_order, message=TEST_PASS_MESSAGE if correct_order else failure_mesage, verbose=verbose)

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
    
    @TestSuite.test
    def check_min_platform_version(self):
        """
        Checks that if pip packages are installed, phantom version > CURRENT_MIN_PHANTOM_VERSION
        """
        msg = TEST_PASS_MESSAGE
        min_version = LooseVersion(self._app_json["min_phantom_version"])
        if min_version < LooseVersion(CURRENT_MIN_PHANTOM_VERSION):
            msg = f'Min Phantom version in app json is too low. Found: "{min_version}" but expected >= "{CURRENT_MIN_PHANTOM_VERSION}"'
        
        return create_test_result_response(success=msg == TEST_PASS_MESSAGE, message=msg)

    @TestSuite.test
    def check_test_connectivity(self): #need to implement
        """
        Checks whether test_connectivity has progress message if it exists
        """
        message = TEST_PASS_MESSAGE
        req_funcs = ["send_progress", "save_progress", "set_status_save_progress"]

        has_test_connectivity = self._has_test_connectivity()
        test_connectivity = self._get_test_connectivity() if has_test_connectivity else False

        if has_test_connectivity and test_connectivity:
            calldefs = self._parser._get_calldefs(test_connectivity)
            for calldef in calldefs:
                func = calldef.func
                name = self._parser.get_id_attr(func)
                if name in req_funcs:
                    break
            else:
                message = "Test connectivity found in JSON, but not in connector"

        else:
            message = "Test connectivity not found in JSON or connector"
        
        return create_test_result_response(success=message==TEST_PASS_MESSAGE, message=message)

    def _has_test_connectivity(self):
        for action in self._parser.app_json["actions"]:
            if action["action"] == "test connectivity":
                return True
        return False

    def _get_test_connectivity(self):
        for funcdef in self._parser.all_funcdefs:
            if funcdef.name.find("test") != -1 and funcdef.name.find("connect") != -1:
                return funcdef
        return False
    
    @TestSuite.test
    def check_valid_app_name_and_guid(self):
        """
        App Name and GUID must be unique, and GUID must be a lowercased string
        """
        app_name = self._app_json["name"]
        app_guid = self._app_json["appid"]

        with self.manage_data_file(APPID_TO_NAME_FILEPATH) as app_guid_to_name:
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

        return create_test_result_response(success=not message, message=TEST_PASS_MESSAGE if not message else message)

    @TestSuite.test(tags=["pre-release"])
    def check_app_package_name(self):
        """
        Package name is unique
        """
        package_name = self._app_json["package_name"]
        app_guid = self._app_json["appid"]

        with self.manage_data_file(APPID_TO_PACKAGE_NAME_FILEPATH) as package_name_map:
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

        return create_test_result_response(success=not message, message=TEST_PASS_MESSAGE if not message else message)

    @TestSuite.test
    def check_action_param_prefixes(self):
        """
        Every parameter has an action_result.parameter associated with it
        """
        app_json_actions = self._app_json.get("actions")
        
        message = TEST_PASS_MESSAGE
        verbose = []
        for action in app_json_actions:
            action_parameters = list(
                action.get("parameters", {}).keys()
            )  # Gets the parameters, if any
            if action_parameters:
                action_output = set(self._get_data_paths(action, parameters=True))
                parameters_formatted = set(
                    f"action_result.parameter.{name}" for name in action_parameters
                )
                output = action_output.symmetric_difference(parameters_formatted)
                if len(output):
                    message = "Action results should contain an action_result.parameter key for every action parameter"
                    verbose.extend(
                        f"Invalid or mismatched action result output {out}" for out in output
                    )
        
        return create_test_result_response(success=not verbose, message=message, verbose=verbose)

    @TestSuite.test(remove_tags=[DEVELOPER_SUPPORTED])
    def check_action_param_matching_contains(self): #will need to implement or get rid of 
        """
        Every parameter for an action with contains has an action_result.parameter with the same contains
        """
        action_list = [
            act
            for act in self._app_json["actions"]
            if act["action"] not in ("test connectivity", "on poll")
        ]
        verbose = []
        for action in action_list:
            data_path_contains = self._get_data_paths(action, contains=True)
            param_contains = {
                param: config["contains"]
                for param, config in action["parameters"].items()
                if config.get("contains")
            }

            for param, contain in param_contains.items():
                action_res_param = f"action_result.parameter.{param}"
                if contain != data_path_contains.get(action_res_param):
                    verbose.append(
                        f"Action '{action["action"]}': parameter '{param}' with contains {contain} does not match output '{action_res_param}' with contains {data_path_contains.get(action_res_param)}"
                    )

        msg = (
            TEST_PASS_MESSAGE
            if not verbose
            else "Action parameter contains should match those belonging to its related action_result.parameter contains"
        )
        return create_test_result_response(success=not verbose, message=msg, verbose=verbose)

    @TestSuite.test
    def check_minimal_data_paths(self):
        """
        Checks to make sure each action includes the minimal required data paths
        """
        app_json_actions = [
            act
            for act in self._app_json["actions"]
            if act["action"] not in ("test connectivity", "on poll")
        ]
        message = None
        verbose = []
        for action in app_json_actions:
            data_paths = set(
                [(path["data_path"], path["data_type"]) for path in self._get_data_paths(action)]
            )
            if not MINIMAL_DATA_PATHS.issubset(data_paths):
                message = "One or more actions are missing a required data path"
                verbose.append(
                    f"{action["action"]} is missing one or more required data path"
                )

        return create_test_result_response(
            success=not verbose, message=TEST_PASS_MESSAGE if not message else message, verbose=verbose,
        )
                
    def _get_data_paths(self, action, parameters=False, contains=False):
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

        action_outputs = {} if contains else []

        action_output_raw = action.get("output")

        if parameters and contains:
            raise ValueError

        if action_output_raw and len(action_output_raw):
            for data_path in action_output_raw:  # Just the data path dict member of the output list
                data_path_value = data_path.get("data_path")
                if data_path_value:  # just the value of the 'data_path' key from the dict
                    if parameters:  # If parameters is passed, then only add parameters to the action_outputs list
                        if data_path_value.startswith("action_result.parameter"):
                            action_outputs.append(data_path_value)
                    elif contains:
                        contains_value = data_path.get("contains")
                        if contains_value and data_path_value.startswith("action_result.parameter"):
                            action_outputs[data_path_value] = contains_value
                    else:
                        action_outputs.append(data_path)

        return action_outputs
    
    @TestSuite.test(critical=False)
    def fields_should_be_passwords(self):
        """
        Fields that look like passwords should be passwords, and passwords should not have 'default' or 'value_list' fields
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
        
        msg = TEST_PASS_MESSAGE if not verbose else "Some configuration parameters may be secrets and should have password data types. Please review"
        return create_test_result_response(success=not verbose, message=msg, verbose=verbose)
