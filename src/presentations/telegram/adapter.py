from __future__ import annotations

from typing import Any, Dict

from infra.errors import BaseError


def format_text_success(message_key: str, data: Dict[str, Any] | None = None) -> str:
    """Format a human-readable success message (placeholder).

    In a real bot, this could use i18n and templates.
    """
    base = message_key.replace("_", " ").capitalize()
    if not data:
        return base
    extra = ", ".join(f"{k}={v}" for k, v in data.items())
    return f"{base}: {extra}"


def format_text_error(error: BaseError) -> str:
    """Format a human-readable error text from BaseError."""
    detail = error.detail or error.detail_key.replace("_", " ")
    return f"{error.message_key.replace('_', ' ').capitalize()}: {detail}"


