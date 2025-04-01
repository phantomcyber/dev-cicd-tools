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
