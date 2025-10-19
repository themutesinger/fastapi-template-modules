from __future__ import annotations

import logging
import logging.config
import os
from typing import Dict, Any


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        # Build a minimal JSON line without extra deps
        payload: Dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "trace": getattr(record, "trace_id", "-"),
            "msg": record.getMessage(),
        }
        return ("{"
                f"\"ts\":\"{payload['ts']}\"," 
                f"\"level\":\"{payload['level']}\"," 
                f"\"logger\":\"{payload['logger']}\"," 
                f"\"trace\":\"{payload['trace']}\"," 
                f"\"msg\":\"{payload['msg'].replace('\\', '\\\\').replace('"', '\\"')}\""
                "}")


def configure_logging(log_level: str | None = None) -> None:
    level_name = (log_level or os.getenv("LOG_LEVEL") or "INFO").upper()

    # Map common level names to numeric levels; default to INFO if unknown
    numeric_level = getattr(logging, level_name, logging.INFO)

    # Base format includes time, level, logger name, trace id (if present), and message
    # The trace id value is expected to be injected by a custom filter later if configured
    base_format = "%(asctime)s | %(levelname)s | %(name)s | trace=%(trace_id)s | %(message)s"

    is_prod = (os.getenv("APP_ENV", "").lower() in ("prod", "production"))

    dict_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": base_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": _JsonFormatter,
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
                "formatter": "json" if is_prod else "standard",
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
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
