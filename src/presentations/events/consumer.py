from __future__ import annotations

import logging
from typing import Any, Dict

from infra.errors import BaseError
from .adapter import to_event_error, to_event_success_payload


logger = logging.getLogger(__name__)


async def handle_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Demo event handler to showcase standardized payloads.

    In real life, wire this to a broker consumer and route by event["type"].
    """
    try:
        # Demo logic: echo back
        result = {"echo": event}
        return to_event_success_payload(result, message_key="ok")
    except BaseError as exc:  # pragma: no cover - demo
        logger.exception("Domain error while handling event")
        return to_event_error(exc)
    except Exception as exc:  # pragma: no cover - demo
        logger.exception("Unexpected error while handling event")
        err = BaseError(detail=str(exc))
        return to_event_error(err)
