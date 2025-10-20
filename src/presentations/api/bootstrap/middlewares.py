from __future__ import annotations

from typing import Iterable, Sequence, TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from presentations.api.middlewares.locale import LocaleMiddleware
from presentations.api.middlewares.trace import TraceIdMiddleware

if TYPE_CHECKING:
    from configs.settings import Settings


def register_middlewares(app: FastAPI, settings: "Settings | None") -> None:
    """Attach core middlewares and optional infra middlewares."""
    app.add_middleware(LocaleMiddleware)
    app.add_middleware(TraceIdMiddleware)

    if not settings:
        return

    _add_cors(app, settings)
    _add_trusted_hosts(app, settings)


def _add_cors(app: FastAPI, settings: "Settings") -> None:
    origins = _clean_values(settings.CORS_ORIGINS)
    if not origins:
        return

    allow_credentials = "*" not in origins
    allow_origins = ["*"] if not allow_credentials else origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=[TraceIdMiddleware.DEFAULT_HEADER],
        max_age=3600,
    )


def _add_trusted_hosts(app: FastAPI, settings: "Settings") -> None:
    hosts = _clean_values(settings.ALLOWED_HOSTS)
    if not hosts or "*" in hosts:
        return

    extras = ("127.0.0.1", "localhost", "testserver")
    ordered = _deduplicate([*hosts, *extras])
    if not ordered:
        return

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ordered)


def _clean_values(values: Iterable[str]) -> list[str]:
    return [value.strip() for value in values if value and value.strip()]


def _deduplicate(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered
