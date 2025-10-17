from __future__ import annotations

from typing import Dict

from .context import get_locale


# Minimal placeholder dictionary. Extend/replace with real i18n.
_MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "validation_failed": "Validation failed",
        "authentication_failed": "Authentication failed",
        "access_denied": "Access denied",
        "resource_not_found": "Resource not found",
        "method_not_allowed": "Method not allowed",
    },
    "ru": {
        "validation_failed": "Ошибка валидации",
        "authentication_failed": "Ошибка аутентификации",
        "access_denied": "Доступ запрещён",
        "resource_not_found": "Ресурс не найден",
        "method_not_allowed": "Метод не разрешён",
    },
}


def translate(key: str, fallback: str | None = None) -> str:
    locale = get_locale()
    bucket = _MESSAGES.get(locale) or _MESSAGES.get("en", {})
    return bucket.get(key) or fallback or key


