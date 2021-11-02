"""
Builds wheel files for the dependencies of an app, specified in requirements.txt, into the wheels/
folder of the app repo, and updates the app's JSON config specifying any generated wheels as pip
dependencies.

NOTE: If running this script with the --repair_wheels flag, make sure the script is executed from
a manylinux2014_x86_64 container https://github.com/pypa/manylinux
"""
import argparse
import json
import logging
import os
import random
import re
import shutil
import string
import subprocess
import sys
from collections import namedtuple

PLATFORM = 'manylinux2014_x86_64'
REPAIRED_WHEELS_REL_PATH = 'repaired-wheels'

WHEEL_PATTERN = re.compile(
    '^(?P<distribution>([A-Z0-9][A-Z0-9._-]*[A-Z0-9]))-([0-9]+\\.?)+-.+\\.whl$',
    re.IGNORECASE)

AppJson = namedtuple('AppJson', ['file_name', 'content'])
APP_JSON_INDENT = 4


def load_app_json(app_dir):
    json_files = [f for f in os.listdir(app_dir)
                  if not f.endswith('.postman_collection.json') and f.endswith('.json')]

    if len(json_files) != 1:
        error_msg = 'Expected a single json file in {} but got {}'.format(app_dir, json_files)
        logging.error(error_msg)
        raise ValueError(error_msg)

    with open(os.path.join(app_dir, json_files[0])) as f:
        return AppJson(json_files[0], json.load(f))


def _repair_wheels(wheels_to_repair, wheels_dir, app_py_version):
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
    for whl in wheels_to_repair:
        logging.info('Checking %s', whl)
        whl_path = os.path.join(wheels_dir, whl)
        if subprocess.run(['auditwheel', 'show', whl_path]).returncode != 0:
            logging.info('Skipping non-platform wheel %s', whl)
        elif app_py_version == '2.7':
            logging.warning('Platform wheel bundling is unsupported for Python2 apps.')
            os.remove(whl_path)
        else:
            repair_result = subprocess.run(['auditwheel', 'repair', whl_path,
                                            '--plat', PLATFORM, '-w', repaired_wheels_dir], capture_output=True)
            if repair_result.returncode != 0:
                logging.warning('Failed to repair platform wheel %s', whl)

            # original wheel will be replaced by repaired wheels written to repaired-wheels/
            os.remove(whl_path)

    if os.path.exists(repaired_wheels_dir):
        for whl in os.listdir(repaired_wheels_dir):
            shutil.move(os.path.join(repaired_wheels_dir, whl), wheels_dir)
        shutil.rmtree(repaired_wheels_dir)


def update_app_json(app_json, app_dir):
    """
    Updates the app's JSON config to specify that the wheels under the
    repo's wheel/ folder be installed as dependencies.

    https://docs.splunk.com/Documentation/Phantom/4.10.7/DevelopApps/Metadata#Specifying_pip_dependencies
    """
    wheel_paths = [{
        'module': WHEEL_PATTERN.match(f).group('distribution'),
        'input_file': 'wheels/{}'.format(f)
    } for f in sorted(os.listdir(os.path.join(app_dir, 'wheels')))]

    app_json.content['pip_dependencies'] = {'wheel': wheel_paths}
    if 'pip3_dependencies' in app_json.content:
        app_json.content['pip3_dependencies'] = {'wheel': wheel_paths}

    with open(os.path.join(app_dir, app_json.file_name), 'w') as out:
        json.dump(app_json.content, out, indent=APP_JSON_INDENT)
        out.write('\n')


def main(args):
    """
    Main entrypoint.
    """
    app_dir, pip_path, repair_wheels = args.app_dir, args.pip_path, args.repair_wheels

    wheels_dir, requirements_file = '{}/wheels'.format(app_dir), '{}/requirements.txt'.format(app_dir)
    logging.info('Building wheels for dependencies in %s into %s', requirements_file, wheels_dir)

    temp_dir = os.path.join(app_dir, ''.join(random.choices(string.digits, k=10)))
    os.mkdir(temp_dir)

    build_result = subprocess.run([pip_path, 'wheel',
                                   '-f', wheels_dir,
                                   '-w', temp_dir,
                                   '-r', requirements_file], capture_output=True)
    if build_result.stdout:
        logging.info(build_result.stdout.decode())
    if build_result.stderr:
        logging.warning(build_result.stderr.decode())

    if build_result.returncode != 0:
        logging.error('Failed to build wheels from requirements.txt. '
                      'This typically occurs when you have a version conflict in requirements.txt or '
                      'you depend on a library requiring external development libraries (eg, python-ldap). '
                      'In the former case, please resolve any version conflicts before re-running this script. '
                      'In the latter case, please manually build the library in a manylinux https://github.com/pypa/manylinux '
                      'container, making sure to first install any required development libraries. If you are unable '
                      'to build a required dependency for your app, please raise an issue in the app repo for further assistance.')
        shutil.rmtree(temp_dir)
        return 0

    app_json = load_app_json(app_dir)
    app_py_version = app_json.content.get('python_version', '2.7')

    if repair_wheels:
        logging.info('Repairing new platform wheels...')
        new_wheels = set(os.listdir(temp_dir))
        if os.path.exists(wheels_dir):
            new_wheels -= set(os.listdir(wheels_dir))

        _repair_wheels(new_wheels, temp_dir, app_py_version)

    if os.path.exists(wheels_dir):
        shutil.rmtree(wheels_dir)
    os.rename(temp_dir, wheels_dir)

    logging.info('Updating app json with latest dependencies...')
    update_app_json(app_json, app_dir)

    return 0


def parse_args():
    help_str = ' '.join(line.strip() for line in __doc__.strip().splitlines())
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument('app_dir', help='Path to the target app directory'),
    parser.add_argument('pip_path', help='Path to the pip installation to use')
    parser.add_argument('--repair_wheels', action='store_true',
                        help='Whether to repair platform wheels with auditwheel'),
    return parser.parse_args()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(parse_args()))