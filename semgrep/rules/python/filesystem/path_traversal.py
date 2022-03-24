import json
import os

from bs4 import UnicodeDammit


def handle_request_1(request):
    payload = json.loads(request.POST.get('payload'))

    # ruleid: path-traversal
    with open(payload) as f:
        f.write('foo')

    if payload.isalnum():
        # ok: path-traversal
        with open(payload) as f:
            f.write('foo')


def handle_request_2(request):
    payload = json.loads(request.POST.get('payload'))
    a = payload.get('a')

    # ruleid: path-traversal
    with open(a) as f:
        f.write('foo')

    if payload.isalnum():
        # ok: path-traversal
        with open(a) as f:
            f.write('foo')


def handle_request_3(request):
    payload = json.loads(request.POST.get('payload'))
    a = payload.get('a')
    b = a.get('b')

    # ruleid: path-traversal
    with open(b) as f:
        f.write('foo')

    if a.isalnum():
        # ok: path-traversal
        with open(b) as f:
            f.write('foo')


def handle_request_4(request):
    payload = json.loads(request.POST.get('payload'))
    a = payload.get('a')
    b = a.get('b')
    c = b.get('c')

    # ruleid: path-traversal
    with open(c) as f:
        f.write('foo')

    if b.isalnum():
        # ok: path-traversal
        with open(c) as f:
            f.write('foo')


def handle_request_5(request):
    payload = json.loads(request.POST.get('payload'))
    a = payload.get('a')
    b = a.get('b')
    c = b.get('c')
    d = c.get('d')

    # ruleid: path-traversal
    with open(d) as f:
        f.write('foo')

    if c.isalnum():
        # ok: path-traversal
        with open(d) as f:
            f.write('foo')


def handle_request_6(request):
    payload = json.loads(request.POST.get('payload'))

    callback_id = dict(payload).get('callback_id')
    callback_json = json.loads(UnicodeDammit(callback_id).unicode_markup)
    asset_id = dict(callback_json).get('asset_id')

    state_filename = "{0}_state.json".format(asset_id)
    apps_directory = os.path.dirname(os.path.abspath(__file__))
    state_path = "{0}/{1}".format(apps_directory, state_filename)

    # ruleid: path-traversal
    with open(state_path) as f:
        f.write('foo')

    if asset_id.isalnum():
        # ok: path-traversal
        with open(state_path) as f:
            f.write('foo')
