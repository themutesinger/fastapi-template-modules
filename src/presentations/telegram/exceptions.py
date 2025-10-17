from __future__ import annotations

import functools
import logging
from typing import Any, Awaitable, Callable, TypeVar

from infra.errors import BaseError
from .adapter import format_text_error


logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Awaitable[str]])


def with_exceptions(func: F) -> F:
    """Decorator to convert domain errors to Telegram-friendly text.

    - Catches BaseError and formats a standardized, user-facing message
    - Logs both domain and unexpected errors with context
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> str:  # type: ignore[override]
        try:
            return await func(*args, **kwargs)
        except BaseError as exc:  # domain/business error
            logger.exception("Domain error in telegram handler")
            return format_text_error(exc)
        except Exception as exc:  # unexpected
            logger.exception("Unexpected error in telegram handler")
            return f"Error: {exc}"

    return wrapper  # type: ignore[return-value]


