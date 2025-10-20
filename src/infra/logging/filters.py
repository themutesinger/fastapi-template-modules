from __future__ import annotations

import logging

from .context import get_trace_id


class TraceIdFilter(logging.Filter):
    """Injects trace_id into log records for formatting.

    Ensures that format strings using %(trace_id)s do not break when not in a request context.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        if not hasattr(record, "trace_id"):
            record.trace_id = get_trace_id()
        return True



