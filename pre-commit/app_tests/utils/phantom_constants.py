import os

DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

SPLUNK_SUPPORTED = "splunk_supported"
DEVELOPER_SUPPORTED = "developer_supported"
PLAYBOOK_REPO_DEFAULT_BRANCH = "next"
GITHUB_APP_REPO_BRANCH = "next"
GITHUB_API_KEY = os.environ.get("SOAR_APPS_GITHUB_KEY")
TEST_PASS_MESSAGE = "OK"
CURRENT_MIN_PHANTOM_VERSION = "6.3.0"
APPID_TO_NAME_FILEPATH = os.path.join(DIR, "data", "appid_to_name.json")
APPID_TO_PACKAGE_NAME_FILEPATH = os.path.join(DIR, "data", "appid_to_package_name.json")
MINIMAL_DATA_PATHS = set(
    [
        ("action_result.status", "string"),
        ("action_result.message", "string"),
        ("summary.total_objects", "numeric"),
        ("summary.total_objects_successful", "numeric"),
    ]
)
PASSWORD_KEYS = ("key", "password", "token", "secret")