import ast
from app_tests.test_suite import TestSuite
import os
import glob
import traceback
from app_tests.utils.phantom_constants import (
    TEST_PASS_MESSAGE,
)
from app_tests.utils import create_test_result_response
import re
from lxml import etree
from pathlib import Path


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
            connector_body = connector_file.read()

        try:
            tree = ast.parse(connector_body)
            function_defs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

            unsafe_get_list = []

            def determine_unsafe_gets(function, opt_params, dict_id, label):
                
                class ContextVisitor(ast.NodeVisitor):
                    def __init__(self):
                        self.safe_keys_stack = []
                    
                    def visit_If(self, node):
                        # Check if the if condition is a key check
                        if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Str):
                            if isinstance(node.test.ops[0], ast.In):
                                self.safe_keys_stack.append(node.test.left.s)
                        self.generic_visit(node)
                        # Pop the safe key context after visiting the if body
                        if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Str):
                            if isinstance(node.test.ops[0], ast.In):
                                self.safe_keys_stack.pop()

                    def visit_Subscript(self, node):
                        #print(f"Visiting subscript: {ast.dump(node)}")  # Debug print statement
                        #print(f"safe stack: {self.safe_keys_stack} and opt_params are {opt_params}")  # Debug print statement
                        if isinstance(node.value, ast.Name) and node.value.id == dict_id:
                            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                                key = node.slice.value
                                if isinstance(node.ctx, ast.Store):
                                    if key in opt_params:
                                        # the optional param has been set so it is no longer optional
                                        opt_params.remove(key)
                                elif isinstance(node.ctx, ast.Load) or isinstance(node.ctx, ast.Del):
                                    if key in opt_params and key not in self.safe_keys_stack:
                                        unsafe_get_list.append(f"{label} on line {node.value.lineno}")
                                    
                        self.generic_visit(node)

                    def visit_Call(self, node):
                        #print(f"Visiting call: {ast.dump(node)}")  # Debug print statement
                        #print(f"safe stack: {self.safe_keys_stack} and opt_params are {opt_params}")  # Debug print statement

                        if isinstance(node.func, ast.Attribute) and node.func.attr == "pop":
                            # ignroing pop calls where a default is set
                            if isinstance(node.func.value, ast.Name) and node.func.value.id == dict_id and len(node.args) < 2:
                                if (
                                    node.args
                                    and isinstance(node.args[0], ast.Constant)
                                    and node.args[0].value in opt_params
                                ):
                                    unsafe_get_list.append(f"{label} on line {node.lineno}")
                        else:
                            print(f"Visiting call: {ast.dump(node)}")  # Debug print statement
                            print(f"safe stack: {self.safe_keys_stack} and opt_params are {opt_params}")  # Debug print statement
                            # function calls that are either self.func() or func()
                            func_name = None
                            if isinstance(node.func, ast.Name):
                                func_name = node.func.id
                            elif isinstance(node.func, ast.Attribute):
                                func_name = node.func.attr
                                
                            print(f"func_name: {func_name} and function_defs: {function_defs}")
                                    
                            if func_name in function_defs:
                                for arg in node.args:
                                    if isinstance(arg, ast.Name) and arg.id == dict_id:
                                        print(f"calling new func{func_name}")
                                        function_body_visitor = ContextVisitor()
                                        function_body_visitor.safe_keys_stack = self.safe_keys_stack.copy()
                                        print(f"undafe get list before {unsafe_get_list}")
                                        function_body_visitor.visit(function_defs[func_name])
                                        print(f"undafe get list after {unsafe_get_list}")
                                
                                
                            
                        self.generic_visit(node)

                context_visitor = ContextVisitor()
                context_visitor.visit(function)
                
                '''
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
                                    if key in opt_params and key not in safe_keys_visitor.safe_keys_stack:
                                        unsafe_get_list.append(
                                            f"{label} on line {node.value.lineno}"
                                        )
                                elif isinstance(node.ctx, ast.Del):
                                    if key in opt_params and key not in safe_keys_visitor.safe_keys_stack:
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
                                    and node.args[0].value in opt_params and node.args[0].value not in safe_keys_visitor.safe_keys_stack
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
                '''
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
    def check_python_package(self):
        """
        Checks for an __init__.py existing in app directory toplevel
        """
        msg = TEST_PASS_MESSAGE
        app_dir = Path(self._app_code_dir)
        if not (init_py := app_dir / "__init__.py").is_file():
            msg = "App repo does not have an `__init__.py` at toplevel. Not a python module. Adding to app directory."
            init_py.touch()

        return create_test_result_response(
            success=msg == TEST_PASS_MESSAGE, message=msg, fixed=True
        )
