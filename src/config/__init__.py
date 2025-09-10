from __future__ import annotations

from typing import Any

from decouplet import config as env


def get_bool(name: str, default: bool = False) -> bool:
    try:
        return env(name, cast=bool, default=default)
    except Exception:
        value = str(env(name, default=str(default))).lower()
        return value in {"1", "true", "yes", "y", "on"}


def get_int(name: str, default: int) -> int:
    return int(env(name, default=str(default)))


def get_float(name: str, default: float) -> float:
    return float(env(name, default=str(default)))


__all__: list[str] = ["env", "get_bool", "get_int", "get_float"]


