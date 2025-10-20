from __future__ import annotations

from typing import Any

import httpx

from infra.errors import BaseError


class ApiClientError(BaseError):
    code = "external_api_error"
    message_key = "external_service_error"
    detail_key = "external_api_error"
    status_code = 502

    def __init__(self, detail: str | None = None, *, meta: dict[str, Any] | None = None) -> None:
        super().__init__(detail=detail, meta=meta)


class ApiNetworkError(ApiClientError):
    code = "external_network_error"
    detail_key = "external_network_error"
    status_code = 503

    def __init__(self, detail: str | None = None, *, meta: dict[str, Any] | None = None) -> None:
        super().__init__(detail=detail or "network_error", meta=meta)


class ApiHTTPError(ApiClientError):
    code = "external_http_error"
    detail_key = "external_http_error"

    def __init__(self, status_code: int, body: str, response: httpx.Response) -> None:
        meta: dict[str, Any] = {"upstream_status": status_code}
        super().__init__(detail=None, meta=meta)
        self.upstream_status = status_code
        self.body = body
        self.response = response


class ApiBadRequestError(ApiHTTPError):
    code = "external_bad_request"
    message_key = "bad_request"
    detail_key = "invalid"
    status_code = 400


class ApiUnauthorizedError(ApiHTTPError):
    code = "external_invalid_credentials"
    message_key = "authentication_failed"
    detail_key = "invalid_credentials"
    status_code = 401


class ApiForbiddenError(ApiHTTPError):
    code = "external_insufficient_permissions"
    message_key = "access_denied"
    detail_key = "insufficient_permissions"
    status_code = 403


class ApiNotFoundError(ApiHTTPError):
    code = "external_not_found"
    message_key = "resource_not_found"
    detail_key = "not_found"
    status_code = 404


class ApiConflictError(ApiHTTPError):
    code = "external_conflict"
    message_key = "conflict"
    detail_key = "unique"
    status_code = 409


class ApiUnprocessableEntityError(ApiHTTPError):
    code = "external_invalid"
    message_key = "validation_failed"
    detail_key = "invalid"
    status_code = 422


HTTP_STATUS_EXCEPTION_MAP: dict[int, type[ApiHTTPError]] = {
    400: ApiBadRequestError,
    401: ApiUnauthorizedError,
    403: ApiForbiddenError,
    404: ApiNotFoundError,
    409: ApiConflictError,
    422: ApiUnprocessableEntityError,
}


def build_http_error(status: int, body: str, response: httpx.Response) -> ApiHTTPError:
    error_cls = HTTP_STATUS_EXCEPTION_MAP.get(status, ApiHTTPError)
    return error_cls(status, body, response)
