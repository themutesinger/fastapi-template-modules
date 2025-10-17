from __future__ import annotations

from .logging_bridge import init_logging
from .sentry import init_sentry


def init_observability(settings) -> None:
    # logging first
    init_logging(settings)
    # sentry second
    init_sentry(settings)


