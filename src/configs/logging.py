from __future__ import annotations

import logging
import logging.config
import os
from typing import Dict, Any


def configure_logging(log_level: str | None = None) -> None:
    level_name = (log_level or os.getenv("LOG_LEVEL") or "INFO").upper()

    # Map common level names to numeric levels; default to INFO if unknown
    numeric_level = getattr(logging, level_name, logging.INFO)

    # Base format includes time, level, logger name, trace id (if present), and message
    # The trace id value is expected to be injected by a custom filter later if configured
    base_format = "%(asctime)s | %(levelname)s | %(name)s | trace=%(trace_id)s | %(message)s"

    dict_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": base_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            # Uvicorn has its own loggers; align formatting for consistency
            "uvicorn": {
                "format": base_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "filters": {
            # Injects trace_id into each record; safe outside request context
            "with_trace": {
                "()": "infra.logging.TraceIdFilter",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "filters": ["with_trace"],
                "level": numeric_level,
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": numeric_level,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": numeric_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": numeric_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": numeric_level,
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(dict_config)


