from http import HTTPStatus

from requests import HTTPError
from requests.adapters import Retry, HTTPAdapter
from requests_toolbelt import sessions


GITHUB_REPO_BASE_URL = 'https://api.github.com/repos/{}/'

COMMIT_AUTHOR = {
    'name': 'root',
    'email': 'root@splunkphantom'
}


class GitHubApiSession:
    """
    Wrapper over an HTTP client to simplify requests to https://docs.github.com/en/rest
    """
    def __init__(self, api_key, repo_name):
        self._api_key = api_key
        self.repo_name = repo_name
        self._repo_base_url = GITHUB_REPO_BASE_URL.format(repo_name)
        self._session = sessions.BaseUrlSession(base_url=self._repo_base_url)
        self._session.headers.update({
            'Authorization': 'Token {}'.format(self._api_key),
            'Accept': 'application/vnd.github.v3+json'
        })
        self._session.hooks['response'] = [lambda resp, *args, **kwargs: resp.raise_for_status()]

        retry_strategy = Retry(total=5,
                               backoff_factor=1,
                               status_forcelist=[HTTPStatus.REQUEST_TIMEOUT,
                                                 HTTPStatus.TOO_MANY_REQUESTS,
                                                 HTTPStatus.INTERNAL_SERVER_ERROR,
                                                 HTTPStatus.BAD_GATEWAY,
                                                 HTTPStatus.SERVICE_UNAVAILABLE,
                                                 HTTPStatus.GATEWAY_TIMEOUT],
                               method_whitelist=['GET', 'PATCH', 'POST'])
        self._session.mount(self._repo_base_url, HTTPAdapter(max_retries=retry_strategy))

    def get(self, path, **kwargs):
        return self._session.get(path, json=kwargs).json()

    def post(self, path, **kwargs):
        return self._session.post(path, json=kwargs).json()

    def patch(self, path, **kwargs):
        return self._session.patch(path, json=kwargs).json()
