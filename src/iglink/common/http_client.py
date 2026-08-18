import requests
from requests import Response


class HttpClient(object):

    def __init__(self, headers):
        self.headers = headers

    def get_request(self, url: str, headers_enabled=True, extra_headers: dict[str, str] = {}) -> Response:
        return self._request("GET", url, headers_enabled, extra_headers)

    def _request(self, method, url, headers_enabled, extra_headers: dict[str, str] = {}) -> Response:
        if headers_enabled:
            headers = self.headers | extra_headers
        else:
            headers = None

        response = None
        try:
            response = requests.request(method, url, headers=headers)
            return response
        except:
            raise RuntimeError(f"Error while request. Original response: {response.text}")
