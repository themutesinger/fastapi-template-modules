from __future__ import annotations

from typing import Callable

from fastapi import Request, Response

from infra.i18n import clear_locale, set_locale


HEADER = "Accept-Language"


def _pick_language(value: str | None) -> str:
    if not value:
        return "en"
    # Very naive parser: take the first tag (e.g., "ru,en;q=0.8" -> "ru")
    return value.split(",", 1)[0].strip() or "en"


async def locale_middleware(request: Request, call_next: Callable[[Request], Response]) -> Response:
    lang = _pick_language(request.headers.get(HEADER))
    set_locale(lang)
    try:
        response = await call_next(request)
    finally:
        clear_locale()
    return response


