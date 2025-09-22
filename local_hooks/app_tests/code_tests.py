import ast
from .test_suite import TestSuite
import os
import glob
import traceback
from .utils.phantom_constants import (
    TEST_PASS_MESSAGE,
)
from .utils import create_test_result_response
import re
from lxml import etree
from pathlib import Path
from typing import Optional


class ContextVisitor(ast.NodeVisitor):
    def __init__(
        self,
        action_opt_params: set,
        config_opt_param: set,
        function_defs: dict[str, ast.AST],
        dict_id: dict[str, set] = {},
        parent: Optional[ast.AST] = None,
    ):
        self.safe_keys_stack = []
        self.dict_id = dict_id
        self.action_opt_params = action_opt_params
        self.config_opt_params = config_opt_param
        self.function_defs = function_defs
        self.unsafe_get_list = []
        self.functions_visited = set()  # helper functions can be called multiple times. This keeps track of the functions that have been visited
        self.parent = parent

    def is_handle_action(self, f_name: str) -> bool:
        for action_id in self.action_opt_params:
            if f_name.endswith(action_id):
                self.dict_id["param"] = self.action_opt_params[action_id]
                return True
        return False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        f_name = node.name
        if f_name in self.functions_visited:
            return

        if self.is_handle_action(f_name) or f_name.startswith("initialize") or self.parent:
            self.functions_visited.add(f_name)
            self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        def is_key_check(condition):
            if isinstance(condition, ast.Compare):
                if (
                    isinstance(condition.left, ast.Constant)
                    and isinstance(condition.ops[0], ast.In)
                    and condition.comparators
                ):
                    # check for key in dict
                    if (
                        isinstance(condition.comparators[0], ast.Name)
                        and condition.comparators[0].id in self.dict_id
                    ):
                        return True
                    elif isinstance(condition.comparators[0], ast.Call) and isinstance(
                        condition.comparators[0].func, ast.Attribute
                    ):
                        # check for key in dict.keys()
                        return (
                            condition.comparators[0].func.attr == "keys"
                            and condition.comparators[0].func.value.id in self.dict_id
                        )
                elif isinstance(condition.left, ast.Call) and isinstance(
                    condition.left.func, ast.Attribute
                ):
                    if (
                        condition.left.func.attr == "get"
                        and condition.left.args
                        and isinstance(condition.left.args[0], ast.Constant)
                    ):
                        if condition.ops and isinstance(condition.ops[0], ast.IsNot):
                            # check for dict.get(key) is not None
                            return (
                                isinstance(condition.left.func.value, ast.Name)
                                and condition.left.func.value.id in self.dict_id
                            )
            elif isinstance(condition, ast.Call):
                if (
                    isinstance(condition.func, ast.Attribute)
                    and condition.func.attr == "get"
                    and condition.args
                    and isinstance(condition.args[0], ast.Constant)
                ):
                    # check for dict.get(key)
                    return (
                        isinstance(condition.func.value, ast.Name)
                        and condition.func.value.id in self.dict_id
                    )

        def get_key_from_call(call):
            if isinstance(call, ast.Call):
                return call.args[0].value
            elif isinstance(call, ast.Compare):
                if isinstance(call.left, ast.Call):
                    return call.left.args[0].value
                else:
                    return call.left.value

        # Check if the if condition is a key check
        if isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.And):
            if all(is_key_check(value) for value in node.test.values):
                for value in node.test.values:
                    self.safe_keys_stack.append(get_key_from_call(value))
        elif is_key_check(node.test):
            self.safe_keys_stack.append(get_key_from_call(node.test))

        self.generic_visit(node)

        # Pop the safe key context after visiting the if body
        if isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.And):
            if all(is_key_check(value) for value in node.test.values):
                for value in node.test.values:
                    self.safe_keys_stack.pop()
        elif is_key_check(node.test):
            self.safe_keys_stack.pop()

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if isinstance(node.value, ast.Name) and node.value.id in self.dict_id:
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                key = node.slice.value
                if isinstance(node.ctx, ast.Store):
                    if key in self.dict_id[node.value.id]:
                        # the optional param has been set so it is no longer optional
                        self.dict_id[node.value.id].remove(key)
                elif isinstance(node.ctx, ast.Load) or isinstance(node.ctx, ast.Del):
                    if key in self.dict_id[node.value.id] and key not in self.safe_keys_stack:
                        self.unsafe_get_list.append(f"Unsafe access on line {node.value.lineno}")

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            if (
                isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == "self"
                and node.value.func.attr == "get_config"
            ):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.dict_id[target.id] = self.config_opt_params

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr == "pop":
            # ignroing pop calls where a default is set
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id in self.dict_id
                and len(node.args) < 2
            ):
                dic_key = node.func.value.id
                if (
                    node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value in self.dict_id[dic_key]
                ):
                    self.unsafe_get_list.append(f"Unsafe access on line {node.lineno}")
        else:
            # function calls that are either self.func() or func()
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in self.function_defs:
                for arg in node.args:
                    if isinstance(arg, ast.Name) and arg.id in self.dict_id:
                        function_body_visitor = ContextVisitor(
                            self.action_opt_params,
                            self.config_opt_params,
                            self.function_defs,
                            self.dict_id,
                            node,
                        )
                        function_body_visitor.functions_visited = self.functions_visited.copy()
                        function_body_visitor.safe_keys_stack = self.safe_keys_stack.copy()
                        function_body_visitor.visit(self.function_defs[func_name])
                        self.functions_visited.update(function_body_visitor.functions_visited)
                        self.unsafe_get_list.extend(function_body_visitor.unsafe_get_list)

        self.generic_visit(node)


class CodeTests(TestSuite):
    def __init__(self, repo_location: Path) -> None:
        super().__init__(repo_location)
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

    @TestSuite.test(critical=False)
    def check_get_opt_params(self):
        """
        Checks if optional parameters are accessed with .get() instead of []
        """

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
            connector_body = connector_file.read()

        try:
            tree = ast.parse(connector_body)
            function_defs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

            context_visitor = ContextVisitor(action_opt_params, config_opt_params, function_defs)
            context_visitor.visit(tree)

        except Exception:
            print("Error processing AST. Printing exception and ignoring...")
            traceback.print_exc()

        failure_message = "Some optional parameters use unsafe getting. Please use `param.get()` or `config.get()` to retrieve optional parameters or change them to required."

        return create_test_result_response(
            success=not context_visitor.unsafe_get_list,
            message=TEST_PASS_MESSAGE if not context_visitor.unsafe_get_list else failure_message,
            verbose=[param for param in context_visitor.unsafe_get_list],
        )

    @TestSuite.test
    def check_light_and_dark_theme_logos(self):
        """
        Validates logos. Verifies both light and dark logos are valid SVG files
        """
        app_json = self._parser.app_json
        verbose = []

        logos = {"Light": app_json.get("logo"), "Dark": app_json.get("logo_dark")}

        for logo_theme, logo_name in logos.items():
            if self._parser.uv_lock_filepath:
                logo_path = self._parser.uv_lock_filepath.parent / logo_name
            else:
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

    def _get_src_dir(self):
        main_module_path = self._parser.sdk_app_json.get("main_module").split(":")[0].split(".")
        main_module_path.pop()
        return self._parser.uv_lock_filepath.parent / "/".join(main_module_path)

    @TestSuite.test
    def check_python_package(self):
        """
        Checks for an __init__.py existing in app directory toplevel
        """
        msg = TEST_PASS_MESSAGE
        app_dir = self._get_src_dir() if self._parser.uv_lock_filepath else Path(self._app_code_dir)
        if not (init_py := app_dir / "__init__.py").is_file():
            msg = "App repo does not have an `__init__.py` at toplevel. Not a python module. Adding to app directory."
            init_py.touch()

        return create_test_result_response(
            success=msg == TEST_PASS_MESSAGE, message=msg, fixed=True
        )
