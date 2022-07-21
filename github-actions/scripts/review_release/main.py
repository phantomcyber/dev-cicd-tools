"""
Determines whether a given app release requires manual review or can be automatically released.
"""
import logging
import os
import re
import sys

import requests
from github import Github

from ..common import get_app_json

COMMIT_STATUS_PATTERN = re.compile(r'(AWS CodeBuild (BuildBatch )?us-west-[1-2] )?\(?(?P<context>[\w-]+)\)?')
REQUIRED_COMMIT_STATUSES = [
    'prodsec-scans',
    'build-app',
    'static-tests',
    'integration-tests',
    'sanity-tests'
]
SPLUNK_BASE_API_URL = os.getenv('SPLUNK_BASE_API_URL', 'https://splunkbase.splunk.com/api/v2/apps')
SPLUNK_SUPPORT_TAG = 'splunk'


def _get_splunk_base_data(app_id):
    params = {'appid': app_id, 'product': 'soar', 'include': 'support', 'offset': 0, 'limit': 1}
    resp = requests.get(SPLUNK_BASE_API_URL, params=params)
    resp.raise_for_status()

    results = resp.json()['results']
    if not results:
        return None
    elif len(results) != 1:
        raise ValueError(f'Expected to find one app on Splunkbase for {app_id} but got: {results}')

    return results[-1]


def review_release(app_repo, app_dir_path, release_git_ref):
    # Require manual approval for Splunk-supported apps
    manual_approval = False
    app_json = get_app_json(app_dir_path)
    splunk_base_data = _get_splunk_base_data(app_json['appid'])

    new_release_splunk_supported = app_json['publisher'].lower() == SPLUNK_SUPPORT_TAG
    curr_splunk_supported = splunk_base_data['support'] == SPLUNK_SUPPORT_TAG

    if curr_splunk_supported and new_release_splunk_supported:
        logging.info('Found %s to be Splunk supported app', app_repo)
        manual_approval = True
    elif not curr_splunk_supported and new_release_splunk_supported:
        logging.info('Newly Splunk supported app requires manual review')
        manual_approval = True
    elif not new_release_splunk_supported and curr_splunk_supported:
        logging.info('Newly %s supported supported app that was previously Splunk supported requires manual review',
                     splunk_base_data['support'])
        manual_approval = True

    commit = app_repo.get_commit(release_git_ref)
    all_statuses = commit.get_combined_status().statuses
    statuses_by_names = {}

    for status in all_statuses:
        match = COMMIT_STATUS_PATTERN.match(status.context)
        if not match:
            continue
        statuses_by_names[match.group('context')] = status

    missing_statuses, unsuccessful_statuses = [], []
    for status_name in REQUIRED_COMMIT_STATUSES:
        status = statuses_by_names.get(status_name)
        if not status:
            missing_statuses.append(status_name)
        elif status.state != 'success':
            unsuccessful_statuses.append(status_name)

    if missing_statuses:
        logging.warning('The following required commit statuses are missing for release %s - %s: %s',
                        release_git_ref, commit.sha, missing_statuses)
        manual_approval = True
    if unsuccessful_statuses:
        logging.warning('The following required commit statuses are unsuccessful for release %s - %s: %s',
                        release_git_ref, commit.sha, unsuccessful_statuses)
        manual_approval = True

    if manual_approval:
        logging.warning('The release of %s %s requires manual approval', app_repo.name, release_git_ref)
        return 1

    logging.info('%s %s can be automatically released!', app_repo.name, release_git_ref)
    return 0


def main():
    logging.getLogger().setLevel(logging.INFO)
    try:
        app_dir_path = os.environ['GITHUB_WORKSPACE']
        app_repo_name = os.environ['APP_REPO']

        github = Github(login_or_token=os.environ['GITHUB_TOKEN'])
        app_repo = github.get_repo(app_repo_name)

        ref = os.environ['GITHUB_REF_NAME']

        return review_release(app_repo, app_dir_path, ref)
    except:
        logging.exception('Review failed unexpectedly')
        return -1


if __name__ == '__main__':
    sys.exit(main())
