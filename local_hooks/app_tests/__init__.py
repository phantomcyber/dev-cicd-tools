import importlib
import pkgutil
import inspect
import os
from types import ModuleType
from typing import Callable, Union
from collections.abc import Iterator

from app_tests.test_suite import TestSuite

# The following constant is a dynamic import of all the tests we have in this test runner
# all scripts that rely on a dynamic loading of tests should use the iterate_all_tests function, which relies on
# the modules in this package
TEST_MODULES: list[ModuleType] = [
    importlib.import_module("." + instance[1], "app_tests")
    for instance in pkgutil.iter_modules([os.path.dirname(__file__)])
    if instance[1].endswith("_tests")
]


def _get_pkg_name(attr: Union[type, ModuleType]) -> str:
    try:
        return attr.__file__.rsplit(".", 1)[0].rsplit("/", 1)[1]  # type: ignore
    except AttributeError:
        return attr.__module__.rsplit(".", 1)[-1]


def get_test_suites() -> Iterator[type[TestSuite]]:
    for module in TEST_MODULES:
        for _, klass in inspect.getmembers(module, inspect.isclass):
            if _get_pkg_name(klass) == _get_pkg_name(module) and issubclass(klass, TestSuite):
                yield klass


def iterate_all_tests() -> Iterator[Callable]:
    """
    Iterate over all tests once
    """
    for suite in get_test_suites():
        yield from suite.get_tests()


def tests_by_name() -> dict[str, Callable]:
    """
    Returns a dictionary of all tests by their name
    """
    return {test.pretty_name: test for test in iterate_all_tests()}
