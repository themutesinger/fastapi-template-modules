from __future__ import annotations

from typing import Iterable

from fastapi import FastAPI

from apps.appconfig import AppConfig
from presentations.api.exception_handlers import get_exception_handlers


def register_exception_handlers(app: FastAPI, configs: Iterable[AppConfig]) -> None:
    """Attach custom exception handlers from feature apps and global layer."""
    for cfg in configs:
        handlers_factory = getattr(cfg, "get_exception_handlers", None)
        if not handlers_factory:
            continue
        for exc_type, handler in (handlers_factory() or {}).items():
            app.add_exception_handler(exc_type, handler)

    for exc_type, handler in get_exception_handlers().items():
        app.add_exception_handler(exc_type, handler)
