from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from configs.logging import configure_logging
from infra.observability.bootstrap import init_observability

if TYPE_CHECKING:
    from configs.settings import Settings


def load_settings() -> Settings | None:
    """Load project settings and initialize shared infrastructure pieces."""
    try:
        from configs import settings as app_settings
    except Exception:
        configure_logging("INFO")
        return None

    configure_logging(app_settings.LOG_LEVEL)
    init_observability(app_settings)

    try:
        from infra.i18n import configure as configure_i18n

        configure_i18n(
            enabled=app_settings.I18N_ENABLED,
            default_locale=app_settings.I18N_DEFAULT_LOCALE,
            fallback_locale=app_settings.I18N_FALLBACK_LOCALE,
            domain=app_settings.I18N_DOMAIN,
            locales_dir=app_settings.I18N_LOCALES_DIR,
        )
    except Exception:
        logging.getLogger(__name__).warning("Failed to initialize i18n", exc_info=True)

    return app_settings
