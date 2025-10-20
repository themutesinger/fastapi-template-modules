
import gettext
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from .context import get_locale

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class TranslatorConfig:
    enabled: bool = True
    default_locale: str = "en"
    fallback_locale: str = "en"
    domain: str = "messages"
    locales_dir: str = "locales"


_config = TranslatorConfig()


def configure(
    *,
    enabled: bool,
    default_locale: str,
    fallback_locale: str,
    domain: str,
    locales_dir: str,
) -> None:
    global _config
    _config = TranslatorConfig(
        enabled=enabled,
        default_locale=default_locale or "en",
        fallback_locale=fallback_locale or "en",
        domain=domain or "messages",
        locales_dir=locales_dir or "locales",
    )
    # Drop cache so new settings take effect
    _load_translation.cache_clear()


@lru_cache(maxsize=16)
def _load_translation(locale: str) -> Optional[gettext.NullTranslations]:
    cfg = _config
    localedir = Path(cfg.locales_dir)
    if not localedir.is_absolute():
        localedir = PROJECT_ROOT / localedir
    try:
        return gettext.translation(
            cfg.domain,
            localedir=str(localedir),
            languages=[locale],
        )
    except FileNotFoundError:
        logger.debug("No translation file for locale %s in %s", locale, localedir)
        return None
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to load translation for locale %s: %s", locale, exc)
        return None


def translate(key: str, fallback: str | None = None, *, locale: str | None = None) -> str:
    cfg = _config
    if not cfg.enabled:
        return fallback or key

    loc = locale or get_locale(cfg.default_locale)
    translator = _load_translation(loc)
    if translator is None and cfg.fallback_locale and cfg.fallback_locale != loc:
        translator = _load_translation(cfg.fallback_locale)

    if translator is None:
        return fallback or key

    try:
        text = translator.gettext(key)
        if not text and fallback:
            return fallback
        return text or fallback or key
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Translation error for key %s (locale=%s): %s", key, loc, exc)
        return fallback or key
