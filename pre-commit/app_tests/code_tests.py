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


class ContextVisitor(ast.NodeVisitor):
    def __init__(self, action_opt_params, config_opt_param, function_defs, dict_id=None, label=None, opt_params=None, parent=None):
        self.safe_keys_stack = []
        self.dict_id = dict_id
        self.opt_params = opt_params
        self.action_opt_params = action_opt_params
        self.config_opt_params = config_opt_param
        self.label = label
        self.function_defs = function_defs
        self.unsafe_get_list = []
        self.functions_visited = set()
        self.parent = parent
        
    def visit_FunctionDef(self, node):
        f_name = node.name
        if f_name in self.functions_visited:
            return
        
        to_parse = False
        if f_name.startswith("initialize"):
            self.dict_id = "config"
            self.opt_params = self.config_opt_params
            self.label = "app configuration"
            to_parse = True
        elif self.parent:
            to_parse = True
        else:
            for action_id in self.action_opt_params:
                if f_name.endswith(action_id):
                    self.dict_id = "param"
                    self.opt_params = self.action_opt_params[action_id]
                    self.label = f"`{action_id}` action parameter"
                    to_parse = True
                    break
        print(f"function name {f_name} to_parse: {to_parse}")
        if to_parse:
            self.functions_visited.add(f_name)
            self.generic_visit(node)                   
    
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
        if isinstance(node.value, ast.Name) and node.value.id == self.dict_id:
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                key = node.slice.value
                if isinstance(node.ctx, ast.Store):
                    if key in self.opt_params:
                        # the optional param has been set so it is no longer optional
                        self.opt_params.remove(key)
                elif isinstance(node.ctx, ast.Load) or isinstance(node.ctx, ast.Del):
                    if key in self.opt_params and key not in self.safe_keys_stack:
                        self.unsafe_get_list.append(f"{self.label} on line {node.value.lineno}")
                    
        self.generic_visit(node)

    def visit_Call(self, node):

        if isinstance(node.func, ast.Attribute) and node.func.attr == "pop":
            # ignroing pop calls where a default is set
            if isinstance(node.func.value, ast.Name) and node.func.value.id == self.dict_id and len(node.args) < 2:
                if (
                    node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value in self.opt_params
                ):
                    self.unsafe_get_list.append(f"{self.label} on line {node.lineno}")
        else:
            # function calls that are either self.func() or func()
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in self.function_defs:
                for arg in node.args:
                    if isinstance(arg, ast.Name) and arg.id == self.dict_id:
                        function_body_visitor = ContextVisitor(self.action_opt_params, self.config_opt_params, self.function_defs, self.dict_id, self.label, self.opt_params, node)
                        function_body_visitor.functions_visited = self.functions_visited.copy()
                        function_body_visitor.safe_keys_stack = self.safe_keys_stack.copy()
                        function_body_visitor.visit(self.function_defs[func_name])
                        self.functions_visited.update(function_body_visitor.functions_visited)
                        self.unsafe_get_list.extend(function_body_visitor.unsafe_get_list)
            
        self.generic_visit(node)


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
            '''
            context_visitor = ContextVisitor(action_opt_params, config_opt_params, function_defs) 
            context_visitor.visit(tree)
            unsafe_get_list.extend(context_visitor.unsafe_get_list)

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
