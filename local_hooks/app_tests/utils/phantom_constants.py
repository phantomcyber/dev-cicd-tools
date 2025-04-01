# Copyright (c) 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pathlib import Path

DIR = Path(__file__).resolve().parents[2]

SPLUNK_SUPPORTED = "splunk_supported"
DEVELOPER_SUPPORTED = "developer_supported"
TEST_PASS_MESSAGE = "OK"
CURRENT_MIN_PHANTOM_VERSION = "6.3.0"
APPID_TO_NAME_FILEPATH = DIR / "data" / "appid_to_name.json"
APPID_TO_PACKAGE_NAME_FILEPATH = DIR / "data" / "appid_to_package_name.json"
MINIMAL_DATA_PATHS = set(
    [
        ("action_result.status", "string"),
        ("action_result.message", "string"),
        ("summary.total_objects", "numeric"),
        ("summary.total_objects_successful", "numeric"),
    ]
)
PASSWORD_KEYS = ("key", "password", "token", "secret")
APP_EXTS = (".py", ".html", ".json", ".svg", ".png")
XSS_INJECTIONS = [
    ("<script>alert('hi')</script>", "<script>alert('hi')"),
    (
        '<a href="&#106;avascript:alert(document.cookie)" target="_self">test</a>',
        "<a href=javascript:alert(document.cookie)",
    ),
    ("<img src=x onerror=alert('1')>", "onerror=alert('1')"),
    ('script src="http://attacker/some.js"></script>', "http://attacker/some.js"),
]
