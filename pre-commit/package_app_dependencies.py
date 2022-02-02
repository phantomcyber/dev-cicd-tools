"""
Builds wheel files for the dependencies of an app, specified in requirements.txt, into the wheels/
folder of the app repo, and updates the app's JSON config specifying any generated wheels as pip
dependencies.

NOTE: If running this script with the --repair_wheels flag, make sure the script is executed from
a manylinux2014_x86_64 container https://github.com/pypa/manylinux
"""
import argparse
import itertools
import json
import logging
import os
import pathlib
import random
import re
import shutil
import string
import subprocess
import sys
from collections import namedtuple
from enum import Enum, unique

PLATFORM = 'manylinux2014_x86_64'
REPAIRED_WHEELS_REL_PATH = 'repaired-wheels'

WHEEL_PATTERN = re.compile(
    r'^(?P<distribution>([A-Z0-9][A-Z0-9._-]*[A-Z0-9]))-([0-9]+\.?)+-'
    r'(?P<python_version>[A-Z0-9]+\.?[A-Z0-9]+)-.+-'
    r'(?P<platform>.+)\.whl$',
    re.IGNORECASE)

Wheel = namedtuple('Wheel', ['file_name', 'distribution', 'python_version', 'platform'])
AppJsonWheelEntry = namedtuple('AppJsonWheel', ['module', 'input_file'])


@unique
class PipDependency(Enum):
    """
    Pip dependency keys in app JSON.
    """
    ANY = 'pip_dependencies'
    PYTHON3 = 'pip3_dependencies'
    PYTHON3_9 = 'pip39_dependencies'


@unique
class CPythonTag(Enum):
    """
    Cpython wheel tags and associated properties.

    NOTE: Definition order matters!
    """
    PY2_PY3 = ('py2.py3', r'py2\.py3', 'shared')
    PY2 = ('py2', r'cp2\d?')
    PY39 = ('py39', r'cp39')
    PY36 = ('py36', r'cp36')
    PY3 = ('py3', r'cp3\d{0,2}')

    def __init__(self, tag, pattern, wheels_dir=None):
        self._tag = tag
        self._pattern = re.compile(pattern)
        self._wheels_dir = wheels_dir if wheels_dir is not None else tag

    @property
    def tag(self):
        return self._tag

    @property
    def pattern(self):
        return self._pattern

    @property
    def wheels_dir(self):
        return self._wheels_dir


AppJson = namedtuple('AppJson', ['file_name', 'content'])
APP_JSON_INDENT = 4


def _load_app_json(app_dir):
    json_files = [f for f in os.listdir(app_dir)
                  if not f.endswith('.postman_collection.json') and f.endswith('.json')]

    if len(json_files) != 1:
        error_msg = 'Expected a single json file in {} but got {}'.format(app_dir, json_files)
        logging.error(error_msg)
        raise ValueError(error_msg)

    with open(os.path.join(app_dir, json_files[0])) as f:
        return AppJson(json_files[0], json.load(f))


def _repair_wheels(wheels_to_check, all_wheels, wheels_dir):
    """
    Uses auditwheel to 1) check for platform wheels depending on external binary dependencies
    and 2) bundle external binary dependencies into the platform wheels in necessary. Repaired
    wheels are placed in a sub dir of wheels_dir by auditwheel, which we then use to replace
    the original wheels at the root level of wheels_dir.

    https://github.com/pypa/auditwheel
    """
    if subprocess.run(['auditwheel', '-V']).returncode != 0:
        logging.warning('auditwheel is not installed or is not supported on the given platform. '
                        'Skipping wheel repairs.')
        return

    repaired_wheels_dir = os.path.join(wheels_dir, REPAIRED_WHEELS_REL_PATH)

    for whl in wheels_to_check:
        logging.info('Checking %s', whl)
        whl_path = os.path.join(wheels_dir, whl.file_name)
        if subprocess.run(['auditwheel', 'show', whl_path]).returncode != 0:
            logging.info('Skipping non-platform wheel %s', whl)
        else:
            repair_result = subprocess.run(['auditwheel', 'repair', whl_path,
                                            '--plat', PLATFORM, '-w', repaired_wheels_dir])
            if repair_result.returncode != 0:
                logging.warning('Failed to repair platform wheel %s', whl)
                continue

            # original wheel will be replaced by repaired wheels written to repaired-wheels/
            os.remove(whl_path)
            all_wheels.remove(whl)

    if os.path.exists(repaired_wheels_dir):
        for whl in os.listdir(repaired_wheels_dir):
            shutil.copyfile(os.path.join(repaired_wheels_dir, whl), os.path.join(wheels_dir, whl))
            match = WHEEL_PATTERN.match(whl)
            all_wheels.add(Wheel(
                whl, match.group('distribution'), match.group('python_version'), match.group('platform')))
        shutil.rmtree(repaired_wheels_dir)


def _remove_platform_wheels(all_built_wheels, new_wheels_dir, existing_app_json_wheel_entries):
    """
    Removes all platform wheels in :param: all_built_wheels from :param: new_wheels_dir

    If there's an existing wheel specified in the app json for a dependency that we just built
    a platform wheel for, then we'll assume the existing wheel is compatible for Phantom and
    return it to indicate that the wheel should not be deleted.
    """
    existing_wheels = {w.module: w for w in existing_app_json_wheel_entries}
    existing_wheels_entries_to_keep = []
    for whl in list(all_built_wheels):
        if whl.platform != 'any':
            logging.info('Removing platform wheel %s', whl.file_name)
            all_built_wheels.remove(whl)
            os.remove(os.path.join(new_wheels_dir, whl.file_name))

            # Check if the app already has a wheel packaged for the given dependency
            # to avoid deleting it
            if whl.distribution in existing_wheels:
                existing_whl_path = existing_wheels[whl.distribution].input_file
                logging.info('Existing wheel for %s to be retained: %s',
                             whl.distribution, existing_whl_path)
                existing_wheels_entries_to_keep.append(
                    AppJsonWheelEntry(whl.distribution, existing_whl_path))

    return existing_wheels_entries_to_keep


def _update_app_json(app_json, pip_dependencies_key, wheel_entries, app_dir):
    """
    Updates the app's JSON config to specify that the wheels under the
    repo's wheel/ folder be installed as dependencies.

    https://docs.splunk.com/Documentation/Phantom/4.10.7/DevelopApps/Metadata#Specifying_pip_dependencies
    """
    wheel_paths = [{
        'module': w.module,
        'input_file': w.input_file
    } for w in sorted(wheel_entries, key=lambda w: w.module)]

    app_json.content[pip_dependencies_key] = {'wheel': wheel_paths}

    with open(os.path.join(app_dir, app_json.file_name), 'w') as out:
        json.dump(app_json.content, out, indent=APP_JSON_INDENT)
        out.write('\n')


def _parse_pip_dependency_wheels(app_json, pip_dependency_key):
    pip_dependencies = app_json.content.get(pip_dependency_key, {'wheel': []})
    return [AppJsonWheelEntry(w['module'], w['input_file'])
            for w in pip_dependencies.get('wheel', [])]


def _copy_new_wheels(new_wheels, new_wheels_dir, app_dir):
    """
    Copies new wheels to the wheels/ directory of the app dir.
    """
    new_wheel_paths = []

    def copy_wheel(wheel_name, dst_path):
        src_fp = os.path.join(new_wheels_dir, wheel_name)
        new_wheel_paths.append(os.path.join('wheels', dst_path))
        logging.info('Writing %s --> %s', wheel_name, new_wheel_paths[-1])
        shutil.copyfile(src_fp, os.path.join(app_dir, new_wheel_paths[-1]))

    # Make sure to write the new wheels under appropriate wheels/(py2|py3|py36|py39|shared) sub paths
    for path in iter(cp_tag.wheels_dir for cp_tag in CPythonTag):
        pathlib.Path(os.path.join(app_dir, 'wheels', path)).mkdir(parents=True, exist_ok=True)

    for whl in new_wheels:
        for cp_tag in CPythonTag:
            if whl.python_version == cp_tag.tag or cp_tag.pattern.match(whl.python_version):
                sub_path = os.path.join(cp_tag.wheels_dir, whl.file_name)
                break
        else:
            raise ValueError('{} has an unexpected python version tag: {}'.format(
                whl.file_name, whl.python_version))

        copy_wheel(whl.file_name, sub_path)

    return new_wheel_paths


def _remove_unreferenced_wheel_paths(app_dir, existing_wheel_paths, new_wheel_paths, wheel_entries_for_other_py_versions):
    """
    Removes wheels from the app directory that will no longer be referenced by in app JSON.
    """
    all_referenced_wheel_paths = set(itertools.chain(
        new_wheel_paths, iter(w.input_file for w in wheel_entries_for_other_py_versions)))
    for path in existing_wheel_paths:
        if path not in all_referenced_wheel_paths:
            logging.info('Removing unreferenced wheel under path %s', path)
            path = os.path.join(app_dir, path)
            if not os.path.exists(path):
                logging.warning('%s does not exist!', path)
                continue
            os.remove(os.path.join(app_dir, path))


def main(args):
    """
    Main entrypoint.
    """
    app_dir, pip_path, repair_wheels, pip_dependencies_key = \
        args.app_dir, args.pip_path, args.repair_wheels, args.pip_dependencies_key

    wheels_dir, requirements_file = '{}/wheels'.format(app_dir), '{}/requirements.txt'.format(app_dir)
    pathlib.Path(wheels_dir).mkdir(exist_ok=True)
    logging.info('Building wheels for %s from %s into %s',
                 pip_dependencies_key, requirements_file, wheels_dir)

    temp_dir = os.path.join(app_dir, ''.join(random.choices(string.digits, k=10)))
    os.mkdir(temp_dir)

    try:
        local_wheel_dirs = []
        for sub_dir in os.listdir(wheels_dir):
            local_wheel_dirs.extend(['-f', os.path.join(wheels_dir, sub_dir)])

        build_result = subprocess.run([pip_path, 'wheel',
                                       '-w', temp_dir,
                                       '-r', requirements_file] + local_wheel_dirs)

        if build_result.returncode != 0:
            logging.error('Failed to build wheels from requirements.txt. '
                          'This typically occurs when you have a version conflict in requirements.txt or '
                          'you depend on a library requiring external development libraries (eg, python-ldap). '
                          'In the former case, please resolve any version conflicts before re-running this script. '
                          'In the latter case, please manually build the library in a manylinux https://github.com/pypa/manylinux '
                          'container, making sure to first install any required development libraries. If you are unable '
                          'to build a required dependency for your app, please raise an issue in the app repo for further assistance.')
            return

        # Some apps may have different dependencies for Python2 and Python3, and
        # we don't want to override the wheels for the Python version we aren't building for
        app_json = _load_app_json(app_dir)

        existing_app_json_wheel_entries = _parse_pip_dependency_wheels(app_json, pip_dependencies_key)
        existing_wheel_paths = set(w.input_file for w in existing_app_json_wheel_entries)

        wheel_file_names = set(os.listdir(temp_dir))
        all_built_wheels = set(Wheel(m.group(), m.group('distribution'), m.group('python_version'), m.group('platform'))
                               for m in (WHEEL_PATTERN.match(f) for f in wheel_file_names))
        updated_app_json_wheel_entries = []

        if repair_wheels:
            logging.info('Repairing new platform wheels...')
            wheels_to_repair, existing_wheel_file_names = [], set(os.path.basename(p) for p in existing_wheel_paths)
            for wheel in all_built_wheels:
                if wheel.file_name not in existing_wheel_file_names:
                    wheels_to_repair.append(wheel)

            _repair_wheels(wheels_to_repair, all_built_wheels, temp_dir)
        else:
            logging.warning('New platform wheels will not be repaired but removed.')
            # Remove any platform wheels for dependencies that we just built, but check for any
            # existing wheels for these given dependencies - we won't replace them
            existing_platform_wheel_entries = _remove_platform_wheels(
                all_built_wheels, temp_dir, existing_app_json_wheel_entries)

            # Ensure the entries in the app JSON for the existing wheels don't get overwritten
            updated_app_json_wheel_entries.extend(existing_platform_wheel_entries)
            existing_wheel_paths -= set(w.input_file for w in existing_platform_wheel_entries)

        # Add the newly built wheels and remove the wheels no longer needed from the wheels folder
        new_wheel_paths = _copy_new_wheels(all_built_wheels, temp_dir, app_dir)

        wheels_for_other_py_versions = list(itertools.chain.from_iterable(
            _parse_pip_dependency_wheels(app_json, pip_dep.value)
            for pip_dep in PipDependency if pip_dep.value != pip_dependencies_key))

        _remove_unreferenced_wheel_paths(app_dir=app_dir,
                                         new_wheel_paths=new_wheel_paths,
                                         existing_wheel_paths=existing_wheel_paths,
                                         wheel_entries_for_other_py_versions=wheels_for_other_py_versions)

        logging.info('Updating app json with latest dependencies...')
        for pair in zip(all_built_wheels, new_wheel_paths):
            updated_app_json_wheel_entries.append(
                AppJsonWheelEntry(pair[0].distribution, pair[1]))
        if sorted(updated_app_json_wheel_entries) == sorted(wheels_for_other_py_versions):
            logging.info('Same wheels found for other python versions. Not introducing a new key.')
        else:
            _update_app_json(app_json, pip_dependencies_key, updated_app_json_wheel_entries, app_dir)
    except Exception:
        logging.exception('Unexpected error')
    finally:
        shutil.rmtree(temp_dir)


def parse_args():
    help_str = ' '.join(line.strip() for line in __doc__.strip().splitlines())
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument('app_dir', help='Path to the target app directory'),
    parser.add_argument('pip_path', help='Path to the pip installation to use')
    parser.add_argument('pip_dependencies_key', choices=[pip_dep.value for pip_dep in PipDependency],
                        help='Key in the app JSON specifying pip dependencies')
    parser.add_argument('--repair_wheels', action='store_true',
                        help='Whether to repair platform wheels with auditwheel'),
    return parser.parse_args()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(parse_args()))
