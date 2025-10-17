from __future__ import annotations

import logging
import uuid
from typing import Callable

from fastapi import Request, Response

from infra.logging import clear_trace_id, set_trace_id


logger = logging.getLogger(__name__)


TRACE_HEADER_INBOUND = "X-Request-ID"
TRACE_HEADER_OUTBOUND = "X-Request-ID"


async def trace_id_middleware(request: Request, call_next: Callable[[Request], Response]) -> Response:
    # Prefer inbound header if present; otherwise generate a UUID4
    inbound_id = request.headers.get(TRACE_HEADER_INBOUND)
    trace_id = inbound_id or uuid.uuid4().hex

    set_trace_id(trace_id)
    try:
        response = await call_next(request)
    finally:
        # Always clear context to avoid leaking between requests on same worker
        clear_trace_id()

    # Reflect the id back to the client and expose it for browsers
    response.headers[TRACE_HEADER_OUTBOUND] = trace_id
    response.headers.setdefault("Access-Control-Expose-Headers", TRACE_HEADER_OUTBOUND)

    return response


