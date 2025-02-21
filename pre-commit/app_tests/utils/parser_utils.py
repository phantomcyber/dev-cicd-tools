import functools
_func_caches = {}
import json
from contextlib import contextmanager

def memoize(func=None, ignore_self=False):
    """
    Memoization decorator for functions that might be useful to remember rather than recompute.
    If ignore_self is set to True, the first arg is ignored when determining whether to recompute. Useful for
    memoizing class functions when you want to remember output across multiple instances
    """
    if func is None:
        return functools.partial(memoize, ignore_self=ignore_self)

    func.cache = {}
    _func_caches[func] = func.cache

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if ignore_self:
            key = str((args[1:], kwargs))
        else:
            key = str((args, kwargs))

        if key not in func.cache:
            func.cache[key] = func(*args, **kwargs)
        return func.cache[key]

    return decorator

def clear_memorization(func):
    """
    Clear the cache for a memoized function
    """
    assert hasattr(func, "cache")
    assert isinstance(func.cache, dict)
    func.cache = {}

def find_app_json_name(json_filenames):
    """
    Given a list of possible json files and the app repo name, return the name of the file
    that is most likely to be the app repo's main module json
    """
    # Multiple json files. Exclude known JSON filenames and expect only one at the end regardless of name.
    # Other places (e.g. Splunkbase) enforce a single top-level JSON file anyways.
    filtered_json_filenames = []
    for fname in json_filenames:
        # Ignore the postman collection JSON files
        if "postman_collection" in fname.lower():
            continue
        filtered_json_filenames.append(fname)

    if len(filtered_json_filenames) == 0:
        raise ValueError("No JSON file found in top level of app repo! Aborting tests...")

    if len(filtered_json_filenames) > 1:
        raise ValueError(
            f"Multiple JSON files found in top level of app repo: {filtered_json_filenames}."
            "Aborting because there should be exactly one top level JSON file."
        )

    # There's only one json file in the top level, so it must be the app's json
    return filtered_json_filenames[0]

@contextmanager
def manage_data_file(data_file_name, save=True):
    """
    Any stateful changes to the data file are managed and saved

    :param basestring data_file_name:
    :rtype: NoneType
    """
    with open(data_file_name) as f:
        data = json.loads(f.read())
    yield data

    if save:
        with open(data_file_name, "w") as f:
            f.write(json.dumps(data, indent=4, sort_keys=True) + "\n")