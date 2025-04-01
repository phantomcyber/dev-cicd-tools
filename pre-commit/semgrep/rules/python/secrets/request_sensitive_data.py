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
import requests as r


class Connector:
    def main(self, method="get"):
        # ruleid: request-sensitive-data
        req_method = getattr(r, method)
        req_method(f"https://api.com/resource?auth={self._secret}")

        # ruleid: request-sensitive-data
        req_method = getattr(r, method)
        req_method(f"https://api.com/resource?auth={self._api_token}")

        # ruleid: request-sensitive-data
        req_method = getattr(r, method)
        req_method(f"https://api.com/resource?auth={self._api_key}")

        # ruleid: request-sensitive-data
        req_method = getattr(r, method)
        req_method(f"https://api.com/resource?auth={self._password}")

        # ruleid: request-sensitive-data
        r.get(f"https://api.com/resource?auth={self._secret}")
        # ruleid: request-sensitive-data
        r.get(f"https://api.com/resource?auth={self._api_token}")
        # ruleid: request-sensitive-data
        r.get(f"https://api.com/resource?auth={self._api_key}")
        # ruleid: request-sensitive-data
        r.get(f"https://api.com/resource?auth={self._password}")

        # ok: request-sensitive-data
        r.get("https://api.com/resource", headers={"Authorization": f"Bearer {self._api_token}"})
