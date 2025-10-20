from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping, Tuple, Type

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import sentry_sdk

from infra.i18n import translate
from infra.errors import BaseError, to_http_response
from presentations.api.schemas.common import ErrorItem

logger = logging.getLogger(__name__)

def _response(message_key: str, errors: List[ErrorItem], status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "message": translate(message_key),
            "errors": [e.model_dump() for e in errors],
        },
    )


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:  # type: ignore[override]
    status = exc.status_code
    # Never propagate original detail to clients to avoid leaking upstream/internal info
    detail = ""

    mapping: Dict[int, Tuple[str, str]] = {
        400: ("bad_request", "invalid"),
        401: ("authentication_failed", "invalid_credentials"),
        403: ("access_denied", "insufficient_permissions"),
        404: ("resource_not_found", "not_found"),
        405: ("method_not_allowed", "method_not_allowed"),
        409: ("conflict", "unique"),
    }
    msg_key, code = mapping.get(status, ("validation_failed", "invalid"))
    # Deliberately avoid fallback to the raw detail to prevent leaking upstream messages
    error_detail = translate(code)
    error = ErrorItem(code=code, detail=error_detail)
    return _response(msg_key, [error], status)


def _map_error_type_to_code(error_type: str, message: str) -> str:
    et = error_type.lower()
    msg = message.lower()
    if "missing" in et or "field required" in msg:
        return "required"
    if "none" in et or "null" in msg or "may not be null" in msg:
        return "null"
    if "string_too_short" in et or "too short" in msg or "min length" in msg:
        return "min_length"
    if "string_too_long" in et or "too long" in msg or "max length" in msg:
        return "max_length"
    if "greater_than_equal" in et or ">=" in msg or "min value" in msg:
        return "min_value"
    if "less_than_equal" in et or "<=" in msg or "max value" in msg:
        return "max_value"
    if et.startswith("type_error") or "type" in et:
        return "invalid"
    return "invalid"


def _flatten_errors(errors: List[Mapping[str, Any]]) -> List[ErrorItem]:
    items: List[ErrorItem] = []
    for err in errors:
        loc = err.get("loc")
        attr = None
        if isinstance(loc, (list, tuple)) and len(loc) > 0:
            path = [str(p) for p in loc if p not in ("body", "query", "path", "header")]
            attr = ".".join(path) if path else None
        msg = str(err.get("msg") or "Invalid")
        typ = str(err.get("type") or "invalid")
        code = _map_error_type_to_code(typ, msg)
        items.append(ErrorItem(code=code, detail=translate(code, fallback=msg), attr=attr))
    return items


async def handle_validation_error(request: Request, exc: RequestValidationError | ValidationError) -> JSONResponse:  # type: ignore[override]
    errors = _flatten_errors(exc.errors())
    return _response("validation_failed", errors, 422)


def get_exception_handlers() -> Mapping[Type[Exception], Any]:
    mapping = {
        HTTPException: handle_http_exception,
        RequestValidationError: handle_validation_error,
        ValidationError: handle_validation_error,
    }
    # Единый хендлер для всех BaseError (транспорт-агностичной доменной ошибки)
    async def handle_base_error(request: Request, exc: BaseError) -> JSONResponse:  # type: ignore[override]
        return to_http_response(exc)

    mapping[BaseError] = handle_base_error

    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
        logger.exception("Unhandled exception during request processing")
        try:
            sentry_sdk.capture_exception(exc)
        except Exception:  # pragma: no cover - defensive
            logger.debug("Failed to report unexpected exception to Sentry.", exc_info=True)
        fallback_msg = "Internal server error"
        message = translate("internal_error", fallback=fallback_msg)
        error = ErrorItem(code="internal_error", detail=message)
        return JSONResponse(
            status_code=500,
            content={
                "message": message,
                "errors": [error.model_dump()],
            },
        )

    mapping[Exception] = handle_unexpected_error
    return mapping
