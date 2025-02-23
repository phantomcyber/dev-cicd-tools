import ast
from app_tests.test_suite import TestSuite
import os
import glob
import traceback
from app_tests.utils.phantom_constants import (
    ACTION_ALIASES,
    TEST_PASS_MESSAGE,
    ACTION_MIN_LOG_COUNT,
    SUPPORTED_LOG_CALLS,
)
from app_tests.utils import create_test_result_response
import re
from lxml import etree
import itertools


class CodeTests(TestSuite):
    def __init__(self, app_repo_name, repo_location, **kwargs):
        super().__init__(app_repo_name, repo_location, **kwargs)
        self._app_consts_fp = (glob.glob(os.path.join(self._app_code_dir, "*consts.py")) or [""])[0]
        self._app_connector_fp = self._parser.connector_filepath

    @staticmethod
    def _check_file_empty(file_path):
        return os.path.isfile(file_path) and os.path.getsize(file_path) == 0

    @TestSuite.test
    def check_empty_consts(self):
        """
        Checks if the consts file for the app is empty
        """
        msg = TEST_PASS_MESSAGE
        if self._check_file_empty(self._app_consts_fp):
            os.remove(self._app_consts_fp)
            msg = "Removed consts file because it was empty"

        success = msg == TEST_PASS_MESSAGE
        return create_test_result_response(success=success, message=msg, fixed=not success)

    @staticmethod
    def _ast_node_has_dict_lookup(test_node, key_str, dict_id):
        def is_dict_lookup(_test_node):
            if isinstance(_test_node, ast.Compare):
                if isinstance(_test_node.left, ast.Name):
                    left = _test_node.left.id
                elif isinstance(_test_node.left, ast.Str):
                    left = _test_node.left.s
                else:
                    return False

                if (
                    all(isinstance(op, ast.In) for op in _test_node.ops)
                    and all(
                        isinstance(n, ast.Name) and n.id == dict_id for n in _test_node.comparators
                    )
                    and left == key_str
                ):
                    return True
                else:
                    return False
            elif isinstance(_test_node, ast.Call):
                if len(_test_node.args) != 1:
                    return False
                elif isinstance(_test_node.args[0], ast.Name):
                    arg = _test_node.args[0].id
                elif isinstance(_test_node.args[0], ast.Str):
                    arg = _test_node.args[0].s
                else:
                    return False

                return (
                    _test_node.func.value.id == dict_id
                    and _test_node.func.attr == "has_key"
                    and arg == key_str
                )
            else:
                return False

        if isinstance(test_node, ast.Compare) or isinstance(test_node, ast.Call):
            return is_dict_lookup(test_node)
        elif isinstance(test_node, ast.BoolOp):
            return any(is_dict_lookup(n) for n in test_node.values)

    @staticmethod
    def _ast_node_under_dict_lookup(node, key_str, dict_id):
        while hasattr(node, "parent"):
            node = node.parent
            if (
                isinstance(node, ast.If) or isinstance(node, ast.IfExp)
            ) and CodeTests._ast_node_has_dict_lookup(node.test, key_str, dict_id):
                return True

        return False

    @TestSuite.test
    def check_get_opt_params(self):
        """
        Checks if optional parameters are accessed with .get() instead of []
        """

        unsafe_get_list = []
        app_config = self._parser.app_json.get("configuration", {})
        config_opt_params = set(
            config_param
            for config_param in app_config
            if not app_config[config_param].get("required")
            and app_config[config_param]["data_type"] != "boolean"
        )
        action_opt_params = {
            action.get("identifier"): set()
            for action in self._parser.app_json.get("actions", {})
            if action.get("identifier")
        }

        for action in self._parser.app_json.get("actions", {}):
            action_id = action.get("identifier", "")
            for param, metadata in action.get("parameters", {}).items():
                if not metadata.get("required") and metadata["data_type"] != "boolean":
                    action_opt_params[action_id].add(param)

        # parse consts file to get const variable mappings to param names
        if self._app_consts_fp:
            with open(self._app_consts_fp) as consts_file:
                for line in consts_file:
                    # get mappings for app config params
                    for param in list(config_opt_params):
                        if f" = '{param}'" in line or f' = "{param}"' in line:
                            parse_const_var = re.search(r".+ \=", line).group()[:-2]
                            config_opt_params.add(parse_const_var)

                    # get mappings for action params
                    for action_id in action_opt_params:
                        for param in list(action_opt_params[action_id]):
                            if f" = '{param}'" in line or f' = "{param}"' in line:
                                parse_const_var = re.search(r".+ \=", line).group()[:-2]
                                action_opt_params[action_id].add(parse_const_var)

        # check connector file for unsafe action param gets
        #   using ast module
        with open(self._app_connector_fp) as connector_file:
            try:
                tree = ast.parse(connector_file.read())
                function_defs = {
                    n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                }

                unsafe_get_list = []

                for f_name, function in function_defs.items():
                    dict_id = None
                    if f_name.startswith("initialize"):
                        dict_id = "config"
                        opt_params = config_opt_params
                        label = "app configuration"
                    else:
                        for action_id in action_opt_params:
                            if f_name.endswith(action_id):
                                dict_id = "param"
                                opt_params = action_opt_params[action_id]
                                label = f"`{action_id}` action parameter"
                                break
                        if not dict_id:
                            continue

                    def determine_unsafe_gets(function, opt_params, dict_id, label):
                        for node in ast.walk(function):
                            if isinstance(node, ast.Subscript):
                                if isinstance(node.value, ast.Name) and node.value.id == dict_id:
                                    if isinstance(node.slice, ast.Constant) and isinstance(
                                        node.slice.value, str
                                    ):
                                        key = node.slice.value
                                        if isinstance(node.ctx, ast.Store):
                                            if key in opt_params:
                                                # optional param has been set so it is no longer optional
                                                opt_params.remove(key)
                                        elif isinstance(node.ctx, ast.Load):
                                            if key in opt_params:
                                                unsafe_get_list.append(
                                                    f"{label} on line {node.value.lineno}"
                                                )
                                        elif isinstance(node.ctx, ast.Del):
                                            if key in opt_params:
                                                unsafe_get_list.append(
                                                    f"{label} on line {node.value.lineno}"
                                                )
                                                opt_params.remove(key)
                            elif isinstance(node, ast.Call):
                                # Method calls
                                if isinstance(node.func, ast.Attribute) and node.func.attr == "pop":
                                    if (
                                        isinstance(node.func.value, ast.Name)
                                        and node.func.value.id == dict_id
                                        and len(node.args) < 2
                                    ):
                                        if (
                                            node.args
                                            and isinstance(node.args[0], ast.Constant)
                                            and node.args[0].value in opt_params
                                        ):
                                            unsafe_get_list.append(f"{label} on line {node.lineno}")
                                else:
                                    # function calls that are either self.func() or func()
                                    func_name = None
                                    if isinstance(node.func, ast.Name):
                                        func_name = node.func.id
                                    elif isinstance(node.func, ast.Attribute):
                                        func_name = node.func.attr

                                    if func_name in function_defs:
                                        for arg in node.args:
                                            if isinstance(arg, ast.Name) and arg.id == dict_id:
                                                determine_unsafe_gets(
                                                    function_defs[func_name],
                                                    opt_params,
                                                    dict_id,
                                                    label,
                                                )

                    determine_unsafe_gets(function, opt_params, dict_id, label)

            except Exception:
                print("Error processing AST. Printing exception and ignoring...")
                traceback.print_exc()

        failure_message = "Some optional parameters use unsafe getting. Please use `param.get()` or `config.get()` to retrieve optional parameters or change them to required."

        return create_test_result_response(
            success=not unsafe_get_list,
            message=TEST_PASS_MESSAGE if not unsafe_get_list else failure_message,
            verbose=[param for param in unsafe_get_list],
        )

    @TestSuite.test
    def submission_contains_source(self):
        """
        Submission contains source code, not compiled files
        """
        msg = TEST_PASS_MESSAGE
        if not any(fname.endswith(".py") for fname in os.listdir(self._app_code_dir)):
            msg = "No python files found in submission. Community submissions should have source files."

        return create_test_result_response(success=msg == TEST_PASS_MESSAGE, message=msg)

    @TestSuite.test(tags=["pre-release"])
    def check_light_and_dark_theme_logos(self):
        """
        Validates logos. Verifies both light and dark logos are valid SVG files
        """
        app_json = self._parser.app_json
        verbose = []

        logos = {"Light": app_json.get("logo"), "Dark": app_json.get("logo_dark")}

        for logo_theme, logo_name in logos.items():
            logo_path = os.path.join(self._app_code_dir, logo_name)
            # Make sure logo exists before checking other things
            if not logo_name:
                # this will be throw as an error in json_tests
                continue

            verbose_template = f"{logo_theme} theme logo with name `{logo_name}` {{}}"

            # Don't even check other things if logo isn't SVG
            if not logo_name.endswith("svg"):
                verbose.append(verbose_template.format("is not SVG"))
                continue

            # Validate logo SVG
            try:
                # Disable entity resolution to avoid for XML entity attacks
                xml_parser = etree.XMLParser(resolve_entities=False)
                svg_tree = etree.parse(logo_path, parser=xml_parser)
                svg_root = svg_tree.getroot()
                prop_error = []
                for prop in ("height", "width"):
                    if not self._get_from_svg_tree(svg_root, prop):
                        prop_error.append(prop)
                if prop_error:
                    verbose.append(
                        verbose_template.format(
                            "is missing required properties: {}".format(", ".join(prop_error))
                        )
                    )

                if self._svg_tree_has_entities(svg_tree):
                    has_entities_verbose_message = verbose_template.format(
                        "contains XML Entity fields. These are not permitted. "
                        "See https://en.wikipedia.org/wiki/XML_external_entity_attack "
                        "for details on why this restriction exists."
                    )
                    verbose.append(has_entities_verbose_message)

            except Exception:
                verbose.append(verbose_template.format("failed to parse as valid SVG"))

        msg = TEST_PASS_MESSAGE if not verbose else "There are problems with the logo files"
        return create_test_result_response(success=not verbose, message=msg, verbose=verbose)

    def _svg_tree_has_entities(self, tree):
        """
        Return True if the SVG tree contains XML entities.

        Used as a check to avoid potential XML entity attacks:
        https://en.wikipedia.org/wiki/XML_external_entity_attack

        Logic from:
        https://github.com/tiran/defusedxml/blob/af1f4cf0c1bd94bc6c8debbd500b02daede92d31/defusedxml/lxml.py#L110
        """
        docinfo = tree.docinfo
        for dtd in docinfo.internalDTD, docinfo.externalDTD:
            if dtd:
                if any(entity for entity in dtd.iterentities()):
                    return True

        return False

    def _get_from_svg_tree(self, tree, prop):
        val = tree.get(prop)
        if val:
            return val
        for child in tree:
            val = self._get_from_svg_tree(child, prop)
            if val:
                return val
        return None

    @TestSuite.test
    def check_min_number_log_statements(self):
        """
        Verifies each action implementation makes at least the
        required minimum number of logging statements
        """
        # If the app is still on Python 2, then we'll pass this check and let the python_version
        # check fail, so that only python_version will need to be added to expected_failures if required.
        if self._parser.app_json.get("python_version") != "3":
            return {"success": True, "message": "Skipping check for Python 2 app."}

        with open(self._app_connector_fp) as f:
            root = ast.parse(f.read())
            connector = None
            for node in root.body:
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if (isinstance(base, ast.Attribute) and base.attr == "BaseConnector") or (
                            isinstance(base, ast.Name) and base.id == "BaseConnector"
                        ):
                            connector = node
                            break
            if not connector:
                return create_test_result_response(
                    success=False,
                    message=f"Could not find connector class definition in {self._app_connector_fp}",
                )

        func_names_to_defs = {
            f.name: f for f in [n for n in connector.body if isinstance(n, ast.FunctionDef)]
        }

        def count_number_log_statements(func_def):
            count, stack = 0, list([(n, func_def.name) for n in func_def.body])
            parent_calls = {func_def.name}
            while stack:
                node, curr_call = stack.pop()
                nested_call = False
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                ):
                    func = node.func
                    if func.value.id == "self" and func.attr in SUPPORTED_LOG_CALLS:
                        count += 1
                    elif (
                        func.value.id == "self"
                        and func.attr not in parent_calls
                        and func.attr in func_names_to_defs
                    ):
                        stack.extend([(n, curr_call) for n in node.args + node.keywords])
                        stack.extend([(n, func.attr) for n in func_names_to_defs[func.attr].body])
                        parent_calls.add(func.attr)
                        nested_call = True
                elif (
                    isinstance(node, ast.Expr)
                    or isinstance(node, ast.Assign)
                    or isinstance(node, ast.AugAssign)
                    or isinstance(node, ast.Return)
                    or isinstance(node, ast.keyword)
                ):
                    stack.append((node.value, curr_call))
                elif (
                    isinstance(node, ast.If)
                    or isinstance(node, ast.For)
                    or isinstance(node, ast.While)
                    or isinstance(node, ast.With)
                ):
                    stack.extend([(n, curr_call) for n in node.body])
                elif isinstance(node, ast.Try):
                    stack.extend(
                        [(n, curr_call) for n in node.body]
                        + list(
                            itertools.chain(
                                *(
                                    [(n, curr_call) for n in handler.body]
                                    for handler in node.handlers
                                )
                            )
                        )
                    )

                if not nested_call and stack and stack[-1][1] != curr_call:
                    parent_calls.remove(curr_call)

            return count

        action_ids = [a["identifier"] for a in self._parser.app_json["actions"]]
        verbose = []

        for action in action_ids:
            expected_func_names = []
            for action_name in [action, *ACTION_ALIASES.get(action, [])]:
                expected_func_names.extend(
                    [f"_handle_{action_name}", f"_{action_name}", action_name]
                )
            func_def = [f for f in [func_names_to_defs.get(n) for n in expected_func_names] if f]
            if not func_def:
                verbose.append(
                    f"Could not find an implementation for {action} "
                    f"under an expected name: {expected_func_names}"
                )
                continue

            func_def = func_def[0]
            log_count = count_number_log_statements(func_def)
            if log_count < ACTION_MIN_LOG_COUNT:
                verbose.append(f"{func_def.name} has too few log statements: {log_count}")

        msg = (
            TEST_PASS_MESSAGE
            if not verbose
            else f"Action implementations should have at least {ACTION_MIN_LOG_COUNT} statements to any of the following logging methods: {sorted(SUPPORTED_LOG_CALLS)}. Note that logging statements appearing in loops are only counted once."
        )
        return create_test_result_response(success=not verbose, message=msg, verbose=verbose)
