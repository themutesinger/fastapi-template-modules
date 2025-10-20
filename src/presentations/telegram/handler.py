from __future__ import annotations

import logging
from typing import Any, Dict

from infra.errors import BaseError
from .adapter import format_text_error, format_text_success
from .exceptions import with_exceptions


logger = logging.getLogger(__name__)


@with_exceptions
async def handle_command(cmd: str, args: Dict[str, Any] | None = None) -> str:
    """Demo Telegram command handler using BaseError for standardized text.

    In real life, wire this into a Telegram bot library and pass updates here.
    """
    if cmd == "/ping":
        return format_text_success("ok", {"pong": True})
    raise BaseError(detail=f"Unknown command: {cmd}")
