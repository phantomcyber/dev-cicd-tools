import glob
import os
import re
import tokenize
from html.parser import HTMLParser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
JINJA_ENV = Environment(loader=FileSystemLoader(os.path.join(SCRIPT_DIR, 'templates')))
LICENSE_TEMPLATE = JINJA_ENV.get_template('LICENSE')


def generate_apache_license_content(copyright_str):

    return LICENSE_TEMPLATE.render(copyright=copyright_str)


SUPPORTED_SOURCE_FILE_EXTENSIONS = ('.py', '.html')

COPYRIGHT_REGEX = re.compile(
    r'^#*\s*(?P<copyright>Copyright\s*(\(c\))?\s*(([0-9]{4},?)+(-[0-9]{4})?)?,?\s*[a-z0-9.,\s]+'
    r',?\s*(([0-9]{4},?)+(-[0-9]{4})?)?)$', re.IGNORECASE)


def update_python_file_copyright(file_path, copyright_str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    replaced_lines = {}

    with open(file_path, 'rb') as src:
        tokens = tokenize.tokenize(src.readline)
        for comment in (t for t in tokens if t.type == tokenize.COMMENT):
            match = COPYRIGHT_REGEX.match(comment.line)
            if match:
                line_number = comment.start[0] - 1  # returned line numbers are 1-indexed
                new_comment = comment.line.replace(match.group('copyright'), copyright_str)
                if new_comment.strip() != comment.line.strip():
                    replaced_lines[line_number] = f'{new_comment}\n'

    if not replaced_lines:
        return False

    with open(file_path, 'r+') as f:
        original_lines = f.readlines()
        f.seek(0)
        f.truncate()
        for i in range(len(original_lines)):
            f.write(replaced_lines.get(i, original_lines[i]))

    return True


class HtmlCopyrightProcessor(HTMLParser):
    def __init__(self, new_copyright_str):
        super().__init__()
        self.new_copyright_str = new_copyright_str
        self.updated_lines = {}

    def feed(self, data):
        self.updated_lines.clear()
        super().feed(data)
        return self.updated_lines
        
    def handle_comment(self, data):
        comment_lines = data.split('\n')
        for i in range(len(comment_lines)):
            match = COPYRIGHT_REGEX.match(comment_lines[i])
            if match:
                new_comment = comment_lines[i].replace(match.group('copyright'),
                                                       self.new_copyright_str)
                if new_comment == comment_lines[i]:
                    continue
                # Check if the comment immediately follows or precedes
                # the start/end of a comment
                if i == 0:
                    new_comment = f'<!--{new_comment}'
                elif i == len(comment_lines) - 1:
                    new_comment = f'{new_comment}-->'

                self.updated_lines[self.lineno - 1 + i] = new_comment


def update_html_file_copyright(file_path, copyright_str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    with open(file_path) as f:
        original_content = f.read()
        original_lines = original_content.split('\n')
        if original_lines[-1] == '':
            original_lines = original_lines[:-1]

    processor = HtmlCopyrightProcessor(copyright_str)
    processor.feed(original_content)

    if not processor.updated_lines:
        return False

    with open(file_path, 'w') as f:
        for i in range(len(original_lines)):
            f.write(f'{processor.updated_lines.get(i, original_lines[i])}\n')

    return True


def update_copyrights(app_dir, copyright_str):
    updated_files = {}

    license_content = generate_apache_license_content(copyright_str)
    license_path = os.path.join(app_dir, 'LICENSE')
    if os.path.isfile(license_path):
        with open(license_path) as f:
            if license_content != f.read():
                updated_files['LICENSE'] = license_content
    else:
        updated_files['LICENSE'] = license_content

    for py_file in glob.glob(os.path.join(app_dir, '*.py')):
        if update_python_file_copyright(py_file, copyright_str):
            with open(py_file) as f:
                updated_files[str(Path(py_file).relative_to(app_dir))] = f.read()

    for html_file in glob.glob(os.path.join(app_dir, '*.html')):
        if update_html_file_copyright(html_file, copyright_str):
            with open(html_file) as f:
                updated_files[str(Path(html_file).relative_to(app_dir))] = f.read()

    return updated_files
