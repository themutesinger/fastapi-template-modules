from __future__ import annotations

import contextvars
from typing import Optional


_locale_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "locale", default=None
)


def get_locale(default: str = "en") -> str:
    value = _locale_var.get()
    return value or default


def set_locale(locale: str) -> None:
    _locale_var.set(locale)


def clear_locale() -> None:
    _locale_var.set(None)


