
import logging
from typing import Any, Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from infra.errors import BaseError
from infra.logging import get_trace_id
from infra.httpx.base.exceptions import ApiHTTPError
logger = logging.getLogger(__name__)
SAFE_REQUEST_KEYS = {"method", "url"}
SAFE_EXTRA_BYTES = 512


def _trim_text(value: str, limit: int = SAFE_EXTRA_BYTES) -> str:
    text = str(value)
    if limit <= 0:
        return text
    if len(text) > limit:
        return text[:limit] + "… (truncated)"
    return text


def init_sentry(settings) -> None:
    """
    Initialize Sentry with safe defaults.

    Drop business-domain errors, redact outbound requests/responses,
    and stamp trace IDs for log correlation.
    """
    if not settings.SENTRY_ENABLED or not settings.SENTRY_DSN:
        return

    environment = settings.SENTRY_ENV or settings.APP_ENV
    default_traces_rate = float(settings.SENTRY_TRACES_SAMPLE_RATE or 0.0)
    default_profiles_rate = float(settings.SENTRY_PROFILES_SAMPLE_RATE or 0.0)

    def _sanitize_request(request: dict[str, Any]) -> dict[str, Any]:
        safe_request = {key: request[key] for key in SAFE_REQUEST_KEYS if key in request}
        url_val = safe_request.get("url")
        if url_val is not None:
            safe_request["url"] = _trim_text(str(url_val))
        return safe_request

    def _sanitize_extra(extra: dict[str, Any]) -> dict[str, Any]:
        safe_extra: dict[str, Any] = {}
        for key, value in extra.items():
            if isinstance(value, str):
                safe_extra[key] = _trim_text(value)
            else:
                safe_extra[key] = value
        return safe_extra

    def _httpx_metadata(exc: ApiHTTPError) -> dict[str, Any]:
        httpx_info: dict[str, Any] = {"status": exc.status_code}
        try:
            if exc.response and exc.response.request:
                httpx_info["url"] = _trim_text(str(exc.response.request.url))
        except Exception:
            logger.debug("Failed to capture HTTPX url for Sentry.", exc_info=True)
        try:
            if exc.response:
                content_type = exc.response.headers.get("Content-Type")
                if content_type:
                    httpx_info["content_type"] = content_type
        except Exception:
            logger.debug("Failed to capture HTTPX headers for Sentry.", exc_info=True)
        return httpx_info

    def before_send(event: dict[str, Any], hint: dict[str, Any]) -> Optional[dict[str, Any]]:
        exc_info = hint.get("exc_info")
        if exc_info and isinstance(exc_info[1], BaseError):
            return None

        try:
            sanitized = dict(event)

            request_data = sanitized.get("request")
            if isinstance(request_data, dict):
                sanitized["request"] = _sanitize_request(request_data)

            extra_data = sanitized.get("extra")
            safe_extra = _sanitize_extra(extra_data) if isinstance(extra_data, dict) else {}
            sanitized["extra"] = safe_extra

            if exc_info and isinstance(exc_info[1], ApiHTTPError):
                exc: ApiHTTPError = exc_info[1]
                safe_extra["httpx"] = _httpx_metadata(exc)

            tags = sanitized.get("tags")
            if not isinstance(tags, dict):
                tags = {}
            tags["trace_id"] = get_trace_id()
            sanitized["tags"] = tags
        except Exception:
            logger.debug("Sentry before_send sanitization failed.", exc_info=True)
            sanitized = event

        return sanitized

    def traces_sampler(sampling_context: dict[str, Any]) -> float:
        tx = sampling_context.get("transaction_context") or {}
        name = (tx.get("name") or "")
        if "health" in name.lower():
            return 0.0
        return default_traces_rate

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=environment,
        release=settings.SENTRY_RELEASE,
        integrations=[FastApiIntegration(), HttpxIntegration(), SqlalchemyIntegration()],
        send_default_pii=bool(settings.SENTRY_SEND_PII),
        traces_sampler=traces_sampler,
        profiles_sample_rate=default_profiles_rate,
        attach_stacktrace=True,
        before_send=before_send,
    )
