import argparse
import json
import time
from app_tests.utils.phantom_constants import (
    SPLUNK_SUPPORTED,
    DEVELOPER_SUPPORTED,
    PLAYBOOK_REPO_DEFAULT_BRANCH,
    GITHUB_APP_REPO_BRANCH
)
from app_tests import get_test_suites, iterate_all_tests

class TestRunner:
    """
    Controller for app testing. Handles selecting and running tests, formatting output, and commiting fixes and db updates
    """

    def __init__(self, app_repo_name, **kwargs):
        self._github = kwargs.pop("github", None) #we need this or self._github_tools to clone the assets and playbook_tests repo to check if we have the min stuff needed
        self._github_tools = kwargs.pop("github_tools", None)

        # Splunk-supported Test Options
        self.test_run_time = int(time.time())

        # General Test Options
        self.mode = kwargs.pop("mode")
        self._app_directory_location = kwargs.pop("app_directory_location")
        self._app_name = app_repo_name
        self._app_repo_name = app_repo_name
        self._playbook_branch = kwargs.pop("playbook_branch", PLAYBOOK_REPO_DEFAULT_BRANCH)
        self._tags = kwargs.pop("tags", [])
        self._test_options = kwargs.pop("tests", None)
        self.results = {}

        # Adding 'mode' parameter in the suite arguments to identify the mode and manage the test on the basis of mode
        self._suite_args = {
            "github": self._github,
            "github_tools": self._github_tools,
            "expect_failures": kwargs.get("expect_failures", False),
            "mode": self.mode,
            "playbook_test_branch": self._playbook_branch,
        }

    def log_result(self, test_name, result, console=True):
        self.results[test_name] = result

        if console:
            success = "PASSED" if result.get("success", False) else "FAILED"
            message = "{} - {:<30}: {}".format(success, test_name, result.get("message", ""))
            print(message)

    def _run_test_from_name(self, local_repo_location, method_name):
        """
        Looks for the location of a method using its name and runs the test
        :param basestring method_name:
        :return dict test_results:
        """
        for suite in self._get_suites(local_repo_location):
            for test in suite.get_tests(self._tags):
                if test.pretty_name == method_name:
                    return test(suite)
        raise AttributeError(f"Could not find method {method_name} anywhere!")

    def _get_suites(self, local_repo_location):
        for suite_cls in get_test_suites():
            yield suite_cls(self._app_name, local_repo_location, **self._suite_args)

    def _run_tests(self, local_repo_location):
        # Run all tests that match our test tags
        if not self._test_options:
            # Old-style output
            for suite in self._get_suites(local_repo_location):
                for idx, test in enumerate(suite.get_tests(self._tags)):
                    if idx == 0:
                        print("{0}\n{1:^55}\n{0}".format("-" * 55, suite.__class__.__name__))
                    return_dict = test(suite)
                    self.log_result(test.pretty_name, return_dict)


        else:
            for test_name in self._test_options:
                return_dict = self._run_test_from_name(local_repo_location, test_name)
                self.log_result(test_name, return_dict)

        exit_code = 0
        for _, result in self.results.items():
            if not (result["success"] or result.get("noncritical", False)):
                exit_code += 1

        return exit_code

    def run(self):

        exit_code = self._run_tests(self._app_directory_location)

        # Auto-raise the merge request based on exit_code returned from the test runs
        # and the flag auto_merge_request if set True

        metadata = {
            "app_name": self._app_name,
            "num_passed": 0,
            "num_failed": 0,
            "num_noncrit_failed": 0,
        }

        for _test, result in self.results.items():
            if result["success"]:
                metadata["num_passed"] += 1
            else:
                if result.get("noncritical", False):
                    metadata["num_noncrit_failed"] += 1
                else:
                    metadata["num_failed"] += 1

        self.results["metadata"] = metadata
        return exit_code, self.results


def create_cmdline_parser(add_help=True):
    parser = argparse.ArgumentParser(
        description="Tests apps according to QA App Testing Template",
        add_help=add_help,
    )

    subparsers = parser.add_subparsers(
        title="Sub Commands",
        description='Type of app under test. Ex: "python test_app.py phantom [options]"',
        help='Help for each command can be viewed with "python test_app.py [COMMAND] --help"',
    )

    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)

    # Splunk supported command options
    splunk_supported_cmd = subparsers.add_parser(
        SPLUNK_SUPPORTED, help="Use this command when testing a Splunk-supported app"
    )
    splunk_supported_cmd.set_defaults(mode=SPLUNK_SUPPORTED, func=run_tests)

    splunk_supported_cmd.add_argument(
        "--no-update-db", action="store_false", help="Don't update app_release data db files"
    )
    splunk_supported_cmd.add_argument("--ova-ip", dest="ip", help="OVA IP of instance")

    _add_common_opts(splunk_supported_cmd, SPLUNK_SUPPORTED)

    # Developer supported command options
    dev_supported_cmd = subparsers.add_parser(
        DEVELOPER_SUPPORTED, help="Use this command when testing a Developer-supported app"
    )
    dev_supported_cmd.set_defaults(mode=DEVELOPER_SUPPORTED, func=run_tests)
    group = dev_supported_cmd.add_mutually_exclusive_group()

    _add_common_opts(dev_supported_cmd, DEVELOPER_SUPPORTED)

    return parser


def _add_common_opts(cmd_parser, tag):
    cmd_parser.add_argument(
        "app_directory", type=str, help="Location for app under test"
    )
    
    cmd_parser.add_argument(
        "--app-repo-name", help="Name of the app repository being tested", required=True
    )
    
    cmd_parser.add_argument(
        "--expect-failures", action="store_true", help="Mark all failures as expected in the db"
    )

    cmd_parser.add_argument(
        "--test-tags",
        dest="tags",
        default=[tag],
        nargs="+",
        help=f'Test tags to run. Default is "{tag}"',
    )
    
    cmd_parser.add_argument(
        "--playbook_branch",
        default=PLAYBOOK_REPO_DEFAULT_BRANCH,
        help="Repo branch to test (default: next)",
    )
    cmd_parser.add_argument(
        "--allow-all-failures",
        action="store_true",
        help=(
            "Pass this flag to make the script give a zero exit code if all tests ran, and a "
            "non-zero exit code only in the case of uncaught exceptions (catastrophic failure)"
        ),
    )

    group = cmd_parser.add_argument_group(
        title="Test Options",
        description="Instead of running all tests, provide flags for test you want to run with flags below",
    )
    for test in iterate_all_tests(tags=[tag]):
        group.add_argument(
            f"--{test.pretty_name}",
            dest="tests",
            action="append_const",
            const=test.pretty_name,
            help=test.__doc__.strip(),
        )


def run_tests(options):
   
    app_name = options["app_repo_name"]
    print("Testing {} app: {}".format(options.get("mode"), app_name))

    exit_code, results = TestRunner(**options).run()

    return (0 if options["allow_all_failures"] else exit_code), results


def process_test_results(results):
    metadata = results.pop("metadata", {})
    results_by_cat = {
        "PASSED": [],
        "FAILED": {"CRITICAL": [], "NONCRITICAL": []},
        "metadata": metadata,
    }
    for test, res in results.items():
        if res["success"]:
            results_by_cat["PASSED"].append(test)
        else:
            if res.get("noncritical", False):
                location = results_by_cat["FAILED"]["NONCRITICAL"]
            else:
                location = results_by_cat["FAILED"]["CRITICAL"]
            location.append({test: res})

    return results_by_cat

def main():

    options = vars(create_cmdline_parser().parse_args())

    if options["debug"]:
        import pudb

        pudb.set_trace()

    exit_code, result = options.pop("func")(options)

    print_result = process_test_results(result)
    print(json.dumps(print_result, indent=4, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    exit(main())
