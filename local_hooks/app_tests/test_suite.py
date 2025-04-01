import functools
from pathlib import Path
import re

from traceback import format_exc
from typing import Callable

from app_tests.utils.app_parser import AppParser, ParserError


class TestSuite:
    """
    Super class for test suite modules. All tests should be wrapped in a subclass of this class
    """

    # Common method name prefixes for tests. Currently only used for tests' pretty names
    test_prefix = re.compile(r"^_?(check|phantom|test)_")

    def __init__(self, repo_location: Path):
        self._app_code_dir = repo_location
        self._parser = AppParser(self._app_code_dir)
        self._app_name = self._parser.app_json["name"].lower()

    @classmethod
    def get_tests(cls) -> list[Callable]:
        """
        Returns a list of test functions in this suite
        :return list of test functions in this suite
        """
        return [getattr(cls, func) for func in dir(cls) if cls._is_test(func)]

    @classmethod
    def _is_test(cls, method):
        """
        Returns True if the given param is the name of a test, or the actual test function, in this suite
        """
        try:
            if not callable(method):
                method = getattr(cls, method)
            return method._is_test
        except AttributeError:
            return False

    @staticmethod
    def test(func=None, critical=True, skip=False, fixable=False):
        """
        Decorator to tag a function in this class as a test

        :param function func: This decorator can be called with no arguments using this param
        :param bool critical: Set to False for tests that should not fail Robot runs
        :param bool skip: Set to True for tests that are unstable or in development and should not be run
        """
        if func is None:
            return functools.partial(TestSuite.test, critical=critical, skip=skip)

        TestSuite._add_attrs_to_test(func, critical, skip)

        @functools.wraps(func)
        def decorator(*args, **kwargs):
            if func.skip:
                # Don't run this test; just mark it as fail and move on
                output = {"success": False, "message": "TEST SKIPPED"}
            else:
                try:
                    # Actually run the test
                    output = func(*args, **kwargs)
                except ParserError as e:
                    # ParserErrors mean issues with the app itself that need to be resolved
                    output = {"success": False, "message": str(e)}
                except Exception:
                    # Catch any execution errors in the test. These need to be fixed when they're found
                    output = {
                        "success": False,
                        "message": "Test execution failed. The Phantom team will resolve this issue",
                        "traceback": format_exc(),
                    }

            output["description"] = func.__doc__.strip()
            output.setdefault("verbose", [output["message"]])
            if not isinstance(output["verbose"], list):
                output["verbose"] = [output["verbose"]]
            if not func.critical:
                output["noncritical"] = True

            return output

        return decorator

    @staticmethod
    def _add_attrs_to_test(func, critical, skip):
        func._is_test = True
        func.skip = skip
        func.critical = critical
        func.pretty_name = TestSuite.test_prefix.sub("", func.__name__)

        if func.skip:
            func.__doc__ = f"TEST SKIPPED. {func.__doc__.strip()}"
