from __future__ import annotations

from typing import Any, Optional
import json

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from infra.errors import BaseError
from infra.logging import get_trace_id
from infra.httpx.base.exceptions import ApiHTTPError
from infra.security.redaction import Redactor, RedactionLevel


def init_sentry(settings) -> None:
    if not settings.SENTRY_ENABLED or not settings.SENTRY_DSN:
        return

    def before_send(event: dict[str, Any], hint: dict[str, Any]) -> Optional[dict[str, Any]]:
        exc_info = hint.get("exc_info")
        if exc_info and isinstance(exc_info[1], BaseError):
            # Drop domain/business errors
            return None
        # Enrich ApiHTTPError with safe httpx response snippet
        if exc_info and isinstance(exc_info[1], ApiHTTPError):
            exc: ApiHTTPError = exc_info[1]
            extra = event.setdefault("extra", {})
            try:
                url = str(exc.response.request.url) if exc.response and exc.response.request else None
            except Exception:
                url = None
            content_type = None
            try:
                content_type = exc.response.headers.get("Content-Type") if exc.response else None
            except Exception:
                pass

            extra["httpx_status"] = exc.status_code
            if url:
                extra["httpx_url"] = url

            # Only attach text/json bodies
            if content_type and (content_type.startswith("application/json") or content_type.startswith("text/")):
                body = exc.body or ""
                # Attempt light redaction for JSON payloads
                if content_type.startswith("application/json"):
                    try:
                        data = json.loads(body)
                        redacted = Redactor.redact(data, level=RedactionLevel.STRICT)
                        body = json.dumps(redacted, ensure_ascii=False)
                    except Exception:
                        # fall back to raw body
                        pass
                extra["httpx_response_body"] = Redactor.shorten(body, 2048)
        # Inject trace_id tag if missing
        event.setdefault("tags", {})["trace_id"] = get_trace_id()
        return event

    def traces_sampler(sampling_context: dict[str, Any]) -> float:
        tx = sampling_context.get("transaction_context") or {}
        name = (tx.get("name") or "").lower()
        if name.startswith("get /health/"):
            return 0.0
        return settings.SENTRY_TRACES_SAMPLE_RATE or 0.0

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=(settings.SENTRY_ENV or settings.APP_ENV),
        release=settings.SENTRY_RELEASE,
        integrations=[FastApiIntegration(), HttpxIntegration(), SqlalchemyIntegration()],
        send_default_pii=bool(settings.SENTRY_SEND_PII),
        traces_sampler=traces_sampler,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE or 0.0,
        attach_stacktrace=True,
        before_send=before_send,
    )


