from __future__ import annotations

from typing import Any, Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from infra.errors import BaseError
from infra.logging import get_trace_id


def init_sentry(settings) -> None:
    if not settings.SENTRY_ENABLED or not settings.SENTRY_DSN:
        return

    def before_send(event: dict[str, Any], hint: dict[str, Any]) -> Optional[dict[str, Any]]:
        exc_info = hint.get("exc_info")
        if exc_info and isinstance(exc_info[1], BaseError):
            # Drop domain/business errors
            return None
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


