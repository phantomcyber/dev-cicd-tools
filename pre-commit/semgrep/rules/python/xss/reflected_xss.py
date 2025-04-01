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
import json

from django.http import HttpResponse


def dangerously_handle_request(request):
    try:
        payload = json.loads(request.POST.get("payload"))
    except Exception as e:
        # ruleid: reflected-cross-site-scripting
        return HttpResponse(f"error: {e}", status=500)

    # ruleid: reflected-cross-site-scripting
    return HttpResponse(payload.get("foobar"), content_type="text/html")


def safely_handle_request(request):
    try:
        payload = json.loads(request.POST.get("payload"))
    except Exception as e:
        # ok: reflected-cross-site-scripting
        return HttpResponse(f"error: {e}", content_type="text/plain", status=500)

    # ok: reflected-cross-site-scripting
    return HttpResponse(payload.get("foobar"), content_type="text/plain")


class RequestHandler:
    def dangerously_handle_request(self):
        try:
            state = json.loads(self._request.GET.get("state"))
        except Exception as e:
            # ruleid: reflected-cross-site-scripting
            return HttpResponse(f"error: {e}", status=500)

        # ruleid: reflected-cross-site-scripting
        return HttpResponse(state, content_type="text/html")

    def safely_handle_request(self):
        try:
            state = json.loads(self._request.GET.get("state"))
        except Exception as e:
            # ok: reflected-cross-site-scripting
            return HttpResponse(f"error: {e}", content_type="text/plain", status=500)

        # ok: reflected-cross-site-scripting
        return HttpResponse(state, content_type="text/plain")
