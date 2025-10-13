import httpx

class ApiClientError(RuntimeError):
    pass


class ApiNetworkError(ApiClientError):
    pass


class ApiHTTPError(ApiClientError):
    def __init__(self, status_code: int, body: str, response: httpx.Response):
        super().__init__(f"HTTP {status_code}: {body}")
        self.status_code = status_code
        self.body = body
        self.response = response