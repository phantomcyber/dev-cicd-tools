import argparse
import dataclasses
import json
from pathlib import Path
import time
from typing import Optional
from collections.abc import Iterable
from app_tests import get_test_suites, iterate_all_tests


class TestRunner:
    """
    Controller for app testing. Handles selecting and running tests, formatting output, and commiting fixes and db updates
    """

    def __init__(self, *, app_directory: Path, tests: Optional[Iterable[str]] = None):
        self.test_run_time = int(time.time())

        # General Test Options
        self._app_directory = app_directory
        self._test_options = set(tests) if tests else None
        self.results = {}

    def log_result(self, test_name, result, console=True):
        self.results[test_name] = result

        if console:
            success = (
                "PASSED"
                if result.get("success", False)
                else "FIXED"
                if result.get("fixed", False)
                else "FAILED"
            )
            message = "{} - {:<30}: {}".format(success, test_name, result.get("message", ""))
            print(message)

    def _get_suites(self, local_repo_location):
        for suite_cls in get_test_suites():
            yield suite_cls(local_repo_location)

    def _run_tests(self, local_repo_location: Path) -> int:
        # Run all tests that match our test options
        for suite in self._get_suites(local_repo_location):
            for idx, test in enumerate(suite.get_tests()):
                if idx == 0:
                    print("{0}\n{1:^55}\n{0}".format("-" * 55, suite.__class__.__name__))

                if self._test_options and test.pretty_name not in self._test_options:
                    continue

                return_dict = test(suite)
                self.log_result(test.pretty_name, return_dict)

        exit_code = 0
        for _, result in self.results.items():
            if not (result["success"] or result.get("noncritical", False)):
                exit_code += 1

        return exit_code

    def run(self) -> tuple[int, dict]:
        exit_code = self._run_tests(self._app_directory)

        metadata = {
            "app_name": self._app_directory.name,
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


@dataclasses.dataclass
class StaticTestArgs:
    app_directory: Path
    tests: list[str] = dataclasses.field(default_factory=list)


def parse_args(add_help: bool = True) -> StaticTestArgs:
    parser = argparse.ArgumentParser(
        description="Tests apps according to QA App Testing Template",
        add_help=add_help,
    )

    parser.add_argument("app_directory", type=Path, help="Location for app under test", default=".")

    group = parser.add_argument_group(
        title="Test Options",
        description="Instead of running all tests, provide flags for test you want to run with flags below",
    )
    for test in iterate_all_tests():
        group.add_argument(
            f"--{test.pretty_name}",
            dest="tests",
            action="append_const",
            const=test.pretty_name,
            help=(test.__doc__ or "").strip(),
        )

    args = StaticTestArgs(**vars(parser.parse_args()))
    if not args.app_directory.is_dir():
        parser.error(f"App directory {args.app_directory} does not exist or is not a directory")

    return args


def process_test_results(results):
    metadata = results.pop("metadata", {})
    results_by_cat = {
        "PASSED": [],
        "FAILED": {"CRITICAL": [], "NONCRITICAL": []},
        "FIXED": [],
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
            if res.get("fixed"):
                results_by_cat["FIXED"].append(test)

    return results_by_cat


def main():
    args = parse_args()
    exit_code, result = TestRunner(**dataclasses.asdict(args)).run()

    print_result = process_test_results(result)
    print(json.dumps(print_result, indent=4, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    exit(main())
