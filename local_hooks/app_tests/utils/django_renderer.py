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
