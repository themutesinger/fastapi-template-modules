
import contextvars
from typing import Optional


# Context variable storing the current request trace id
trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_id", default=None
)


def get_trace_id() -> str:
    value = trace_id_var.get()
    return value or "-"


def set_trace_id(trace_id: str) -> None:
    trace_id_var.set(trace_id)


def clear_trace_id() -> None:
    trace_id_var.set(None)



