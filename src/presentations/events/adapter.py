
from typing import Any, Dict, Mapping

from infra.errors import BaseError, to_event_error_payload


def to_event_success_payload(data: Any, *, message_key: str = "ok", meta: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Standardized successful event payload.

    Mirrors the error shape by including message/meta for consistency.
    """
    return {
        "message": message_key,
        "data": data,
        "meta": dict(meta or {}),
    }


def to_event_error(error: BaseError) -> Dict[str, Any]:
    """Standardized error payload for events using BaseError."""
    return to_event_error_payload(error)


