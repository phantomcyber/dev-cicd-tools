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
import django
import os
from django.conf import settings as django_settings
from django.template import Template, Context

args = {
    "INSTALLED_APPS": [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.humanize",
    ],
    "TEMPLATES": [{"BACKEND": "django.template.backends.django.DjangoTemplates"}],
}

django_settings.configure(**args)
django.setup()


def render_template(template_or_template_path, context_dictionary, output_file=None):
    if os.path.exists(template_or_template_path):
        with open(template_or_template_path) as f:
            template = f.read()
    else:
        template = template_or_template_path

    populated_html = Template(template).render(Context(context_dictionary))
    if output_file is None:
        return populated_html
    else:
        with open(output_file, "w") as f:
            f.write(populated_html)
