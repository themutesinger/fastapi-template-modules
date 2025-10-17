from __future__ import annotations

from typing import Any, Dict


class BaseError(Exception):
    """Transport-агностичная доменная ошибка с кодами для стандартизованных ответов."""

    code: str = "invalid"
    message_key: str = "validation_failed"
    detail_key: str = "invalid"
    meta: Dict[str, Any] | None = None

    def __init__(self, detail: str | None = None, meta: Dict[str, Any] | None = None) -> None:
        self.detail = detail
        self.meta = meta or {}


HTTP_STATUS_MAP: Dict[str, int] = {
    "not_found": 404,
    "unique": 409,
    "invalid_credentials": 401,
    "insufficient_permissions": 403,
    # По умолчанию бизнес-валидация
}


def to_http_response(error: BaseError):
    from fastapi.responses import JSONResponse
    from presentations.api.schemas.common import ErrorItem
    from infra.i18n import translate

    status_code = HTTP_STATUS_MAP.get(error.code, 422)
    detail = error.detail or translate(error.detail_key)
    item = ErrorItem(code=error.code, detail=detail)
    return JSONResponse(
        status_code=status_code,
        content={
            "message": error.message_key,
            "errors": [item.model_dump()],
        },
    )


def to_event_error_payload(error: BaseError) -> Dict[str, Any]:
    from infra.i18n import translate

    return {
        "message": error.message_key,
        "errors": [
            {
                "code": error.code,
                "detail": error.detail or translate(error.detail_key),
                "attr": None,
            }
        ],
        "meta": error.meta or {},
    }


