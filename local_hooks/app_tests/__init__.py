import importlib
from pathlib import Path
import pkgutil
import inspect
from types import ModuleType
from typing import Callable, Optional, Union
from collections.abc import Iterator
from .test_suite import TestSuite

# The following constant is a dynamic import of all the tests we have in this test runner
# all scripts that rely on a dynamic loading of tests should use the iterate_all_tests function, which relies on
# the modules in this package
_TEST_MODULES: Optional[list[ModuleType]] = None


def test_modules() -> list[ModuleType]:
    global _TEST_MODULES
    if _TEST_MODULES is None:
        pkg_dir = Path(__file__).parent
        _TEST_MODULES = [
            importlib.import_module(f".{info.name}", __package__)
            for info in pkgutil.iter_modules([str(pkg_dir)])
            if info.name.endswith("_tests")
        ]
    return _TEST_MODULES


def _get_pkg_name(attr: Union[type, ModuleType]) -> str:
    try:
        return attr.__file__.rsplit(".", 1)[0].rsplit("/", 1)[1]  # type: ignore
    except AttributeError:
        return attr.__module__.rsplit(".", 1)[-1]


def get_test_suites() -> Iterator[type[TestSuite]]:
    for module in test_modules():
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
