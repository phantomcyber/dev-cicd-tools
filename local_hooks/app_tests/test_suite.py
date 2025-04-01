import functools
import re
import inspect

from traceback import format_exc

from app_tests.utils.app_parser import AppParser, ParserError
from app_tests.utils.phantom_constants import (
    SPLUNK_SUPPORTED,
    DEVELOPER_SUPPORTED,
)

# Default tags for tests in all suites
default_tags = [SPLUNK_SUPPORTED, DEVELOPER_SUPPORTED]


class TestSuite:
    """
    Super class for test suite modules. All tests should be wrapped in a subclass of this class
    """

    # Common method name prefixes for tests. Currently only used for tests' pretty names
    test_prefix = re.compile(r"^_?(check|phantom|test)_")

    def __init__(self, app_repo_name, repo_location, **kwargs):
        # Save args used for Robot suite conversion
        self._kwargs = dict(kwargs)

        self._app_repo_name = app_repo_name
        self._app_code_dir = repo_location

        self._parser = AppParser(self._app_code_dir)
        self._app_name = self._parser.app_json["name"].lower()

    @classmethod
    def get_tests(cls, tags=None):
        """
        Returns a list of test functions in this suite
        :return list of test functions in this suite
        """
        if tags is None:
            tags = []
        all_tests = (getattr(cls, func) for func in dir(cls) if cls._is_test(func))
        if tags:
            return (test for test in all_tests if set(tags).intersection(test.tags))
        return all_tests

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
    def test(func=None, tags=None, critical=True, skip=False, remove_tags=None, fixable=False):
        """
        Decorator to tag a function in this class as a test

        :param function func: This decorator can be called with no arguments using this param
        :param list tags: List of custom tags to add to this test case. Extends suite-level tags
        :param bool critical: Set to False for tests that should not fail Robot runs
        :param bool skip: Set to True for tests that are unstable or in development and should not be run
        """
        if remove_tags is None:
            remove_tags = []
        if tags is None:
            tags = []
        if func is None:
            return functools.partial(
                TestSuite.test, tags=tags, critical=critical, skip=skip, remove_tags=remove_tags
            )

        TestSuite._add_attrs_to_test(func, tags, critical, skip, remove_tags)

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
    def _add_attrs_to_test(func, tags, critical, skip, remove_tags):
        func._is_test = True
        func.skip = skip
        func.critical = critical
        func.pretty_name = TestSuite.test_prefix.sub("", func.__name__)

        # Handle all the tags for this test. Start with custom tags
        func.tags = set(tag.lower() for tag in tags)

        # Union with module's default tags if present, else TestSuite's default tags
        module = inspect.getmodule(func)
        try:
            add_tags = module.default_tags
        except AttributeError:
            add_tags = default_tags
        finally:
            func.tags |= set(tag.lower() for tag in add_tags)

        # Pull test type from module docstring if present and add it as a tag
        try:
            test_type = re.search(r"Test Type: (\w+)", module.__doc__).group(1)
        except Exception:
            pass
        else:
            func.tags.add(test_type.lower())

        # Tag for non-criticality
        if not func.critical:
            func.tags.add("noncritical")

        # Tag for skipping. Also, if skip, expand remove_tags to be essentially everything
        if func.skip:
            func.tags.add("skipped")
            # Have to create a new object here because Python reuses the memory address for remove_tags...
            remove_tags = list(set(remove_tags) | {SPLUNK_SUPPORTED, DEVELOPER_SUPPORTED})
            func.__doc__ = "TEST SKIPPED. " + func.__doc__.strip()

        # Remove any tags found in remove_tags
        func.tags -= set(tag.lower() for tag in remove_tags)
