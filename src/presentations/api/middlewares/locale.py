
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from infra.i18n import clear_locale, set_locale


HEADER = "Accept-Language"


def _pick_language(value: str | None) -> str:
    if not value:
        return "en"
    # Very naive parser: take the first tag (e.g., "ru,en;q=0.8" -> "ru")
    return value.split(",", 1)[0].strip() or "en"


class LocaleMiddleware(BaseHTTPMiddleware):
    """Set the current locale for the lifetime of the request."""

    def __init__(self, app: ASGIApp, *, header: str = HEADER) -> None:
        super().__init__(app)
        self.header = header

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore[override]
        lang = _pick_language(request.headers.get(self.header))
        set_locale(lang)
        try:
            response = await call_next(request)
        finally:
            clear_locale()
        return response


__all__ = ["LocaleMiddleware"]


