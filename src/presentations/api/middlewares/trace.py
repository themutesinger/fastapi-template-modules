
import logging
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from infra.logging import clear_trace_id, set_trace_id


logger = logging.getLogger(__name__)


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Attach a request trace identifier to logs and responses."""

    DEFAULT_HEADER = "X-Request-ID"

    def __init__(
        self,
        app: ASGIApp,
        *,
        inbound_header: str | None = None,
        outbound_header: str | None = None,
    ) -> None:
        super().__init__(app)
        self.inbound_header = inbound_header or self.DEFAULT_HEADER
        self.outbound_header = outbound_header or self.inbound_header

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore[override]
        inbound_id = request.headers.get(self.inbound_header)
        trace_id = inbound_id or uuid.uuid4().hex

        set_trace_id(trace_id)
        try:
            response = await call_next(request)
        finally:
            clear_trace_id()

        self._set_response_headers(response, trace_id)
        return response

    def _set_response_headers(self, response: Response, trace_id: str) -> None:
        response.headers[self.outbound_header] = trace_id

        expose_header = response.headers.get("Access-Control-Expose-Headers")
        if not expose_header:
            response.headers["Access-Control-Expose-Headers"] = self.outbound_header
            return

        exposed = {value.strip() for value in expose_header.split(",") if value.strip()}
        if self.outbound_header not in exposed:
            exposed.add(self.outbound_header)
            response.headers["Access-Control-Expose-Headers"] = ", ".join(sorted(exposed))


__all__ = ["TraceIdMiddleware"]
