import importlib
import pkgutil
import inspect

import os

from app_tests.test_suite import TestSuite, default_tags


# The following constant is a dynamic import of all the tests we have in this test runner
# all scripts that rely on a dynamic loading of tests should use the iterate_all_tests function, which relies on
# the modules in this package
TEST_MODULES = [
    importlib.import_module("." + instance[1], "app_tests")
    for instance in pkgutil.iter_modules([os.path.dirname(__file__)])
    if instance[1].endswith("_tests")
]


def _get_pkg_name(attr):
    try:
        return attr.__file__.rsplit(".", 1)[0].rsplit("/", 1)[1]
    except AttributeError:
        return attr.__module__.rsplit(".", 1)[-1]


def get_test_suites(tags=None):
    for module in TEST_MODULES:
        for _, klass in inspect.getmembers(module, inspect.isclass):
            if _get_pkg_name(klass) == _get_pkg_name(module) and issubclass(klass, TestSuite):
                if tags is not None:
                    try:
                        defaults = set(module.default_tags)
                    except AttributeError:
                        defaults = set(default_tags)
                    finally:
                        if set(tags).intersection(defaults):
                            yield klass
                else:
                    yield klass


def iterate_all_tests(tags=None):
    """
    Iterate over all tests once
    """
    for suite in get_test_suites():
        yield from suite.get_tests(tags)