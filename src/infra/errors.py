from __future__ import annotations

import logging
import warnings
from typing import Any, Dict

from infra.i18n import translate

_logger = logging.getLogger(__name__)

class BaseError(Exception):
    """Transport-agnostic domain error with standardized response metadata."""

    code: str = "invalid"
    message_key: str = "validation_failed"
    detail_key: str = "invalid"
    status_code: int = 422
    __abstract__: bool = True

    def __init_subclass__(cls, *, abstract: bool | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abstract is not None:
            cls.__abstract__ = abstract
        else:
            cls.__abstract__ = cls.__dict__.get("__abstract__", False)

        if cls.__abstract__:
            return

        required_attrs = ("code", "message_key", "detail_key")
        for attr in required_attrs:
            base_value = getattr(BaseError, attr)
            child_value = getattr(cls, attr, None)
            if child_value == base_value:
                warnings.warn(
                    f"Class {cls.__name__} should override '{attr}' (currently {base_value!r}).",
                    UserWarning,
                    stacklevel=2,
                )

    def __init__(
        self,
        detail: str | None = None,
        *,
        attr: str | None = None,
        meta: Dict[str, Any] | None = None,
    ) -> None:
        if detail is not None:
            _logger.warning(
                "Custom error detail provided for %s: %s",
                self.__class__.__name__,
                detail,
            )

        self.detail = detail
        self.attr = attr
        self.meta = dict(meta or {})
        rendered = detail or self.detail_key
        super().__init__(rendered)
        self.args = (rendered,)


HTTP_STATUS_MAP: Dict[str, int] = {
    "not_found": 404,
    "unique": 409,
    "invalid_credentials": 401,
    "insufficient_permissions": 403,
}


def to_http_response(error: BaseError):
    from fastapi.responses import JSONResponse
    from presentations.api.schemas.common import ErrorItem

    status_code = getattr(error, "status_code", None) or HTTP_STATUS_MAP.get(error.code, 422)
    detail = error.detail or translate(error.detail_key)
    item = ErrorItem(code=error.code, detail=detail, attr=error.attr)
    return JSONResponse(
        status_code=status_code,
        content={
            "message": translate(error.message_key),
            "errors": [item.model_dump()],
        },
    )


def to_event_error_payload(error: BaseError) -> Dict[str, Any]:
    return {
        "message": translate(error.message_key),
        "errors": [
            {
                "code": error.code,
                "detail": error.detail or translate(error.detail_key),
                "attr": error.attr,
            }
        ],
        "meta": error.meta or {},
    }
