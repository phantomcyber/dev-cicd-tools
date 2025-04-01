from app_tests.test_suite import TestSuite
import re
from app_tests.utils.phantom_constants import XSS_INJECTIONS, TEST_PASS_MESSAGE
from app_tests.utils.django_renderer import render_template
from app_tests.utils import create_test_result_response


class SecurityTests(TestSuite):
    def __init__(self, app_repo_name, repo_location, **kwargs):
        super().__init__(app_repo_name, repo_location, **kwargs)

    @TestSuite.test
    def check_xss_custom_views(self):
        """
        No XSS ability given custom django views
        """
        # try to brute force contexts with XSS tags and see what happens
        # try to see if the flask XSS project raises any errors
        verbose = []
        for file, contents in self._parser.files.items():
            if file.endswith(".html"):
                # need to get template vars in a better manner
                for match in re.finditer(r"{{\s+([\w\d_]+)\s+}}", contents):
                    for xss_attack, xss_success in XSS_INJECTIONS:
                        try:
                            singleton_variable = match.group(1)
                            rendered_result = render_template(
                                contents, {singleton_variable: xss_attack}
                            )
                        except Exception:
                            continue

                        # if empty string, assume we want to check straight match
                        xss_success = xss_success if xss_success else xss_attack
                        if xss_success in rendered_result:
                            verbose.append((xss_attack, singleton_variable, file))
                            break

        fail_msg = "There are some potential XSS injections in your custom templates"
        return create_test_result_response(
            success=not verbose,
            message=TEST_PASS_MESSAGE if not verbose else fail_msg,
            verbose=[
                "Applying `{}` to `{}` in `{}` can result in potential XSS".format(*args)
                for args in verbose
            ],
        )

    @TestSuite.test(critical=False)
    def check_malicious_html(self):
        """
        App JSON has no malicious HTML
        """
        malicious_files = []
        for file, contents in self._parser.files.items():
            if file.endswith(".html"):
                if re.search(r"autoescape\s+off", contents):
                    malicious_files.append(("autoescape", file))

                if re.search(r"\|safe\|", contents):
                    malicious_files.append(("safe", file))

        no_template_manipulation = not bool(malicious_files)
        failure_message = "Templates have (potentially) unneeded escape tags"

        return create_test_result_response(
            success=no_template_manipulation,
            message=TEST_PASS_MESSAGE if no_template_manipulation else failure_message,
            verbose=[
                f"Tag `{tag}` found in {file_path}, which may lead to vulnerable views"
                for tag, file_path in malicious_files
            ],
        )

    @TestSuite.test
    def splunk_supported_debug_print(self):
        """
        Checks for stray/bad authentication and/or headers dump in app code
        """
        verbose = []
        fix_lines = []
        funcs = set(["debug_print"])
        bad_args = set(["headers", "auth", "password", "token", "secret"])

        for calldef in self._parser.all_calldefs:
            func_name = self._parser.get_id_attr(calldef.func)
            if func_name.issubset(funcs):
                for arg in calldef.args:
                    arg_name = self._parser.get_id_attr(arg)
                    if arg_name and arg_name.issubset(bad_args):
                        verbose.append(
                            f"Found insecure argument {arg_name} passed to function {func_name}"
                        )
                        fix_lines.append(calldef.lineno)

        return create_test_result_response(
            success=not verbose,
            message=TEST_PASS_MESSAGE
            if not verbose
            else "Insecure debug prints found in connector",
            verbose=verbose,
        )
