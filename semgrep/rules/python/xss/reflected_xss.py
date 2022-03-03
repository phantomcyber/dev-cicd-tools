import json

from django.http import HttpResponse


def dangerously_handle_request(request):
    try:
        payload = json.loads(request.POST.get('payload'))
    except Exception as e:
        # ruleid: reflected-cross-site-scripting
        return HttpResponse(f'error: {e}', status=500)

    # ruleid: reflected-cross-site-scripting
    return HttpResponse(payload.get('foobar'), content_type = "text/html")


def safely_handle_request(request):
    try:
        payload = json.loads(request.POST.get('payload'))
    except Exception as e:
        # ok: reflected-cross-site-scripting
        return HttpResponse(f'error: {e}', content_type='text/plain', status=500)

    # ok: reflected-cross-site-scripting
    return HttpResponse(payload.get('foobar'), content_type = "text/plain")


class RequestHandler:
    def dangerously_handle_request(self):
        try:
            state = json.loads(self._request.GET.get('state'))
        except Exception as e:
            # ruleid: reflected-cross-site-scripting
            return HttpResponse(f'error: {e}', status=500)

        # ruleid: reflected-cross-site-scripting
        return HttpResponse(state, content_type="text/html")

    def safely_handle_request(self):
        try:
            state = json.loads(self._request.GET.get('state'))
        except Exception as e:
            # ok: reflected-cross-site-scripting
            return HttpResponse(f'error: {e}', content_type='text/plain', status=500)

        # ok: reflected-cross-site-scripting
        return HttpResponse(state, content_type="text/plain")


from phantom import BaseConnector as Base


class Connector(Base):
    def handle_request(self):
        # ok: reflected-cross-site-scripting
        return HttpResponse('foobar')
