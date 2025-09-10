from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from typing import Any, TypeVar, cast

from .repository import CompositeRepository, EnvRepository, RepositorySecret

T = TypeVar("T")

_TRUE_VALUES = {"1", "true", "yes", "y", "on"}
_FALSE_VALUES = {"0", "false", "no", "n", "off"}


# Build a composite repository: process env first, then secrets directory.
_SECRETS_PATH = os.getenv("SECRETS_PATH", "/run/secrets/")
_REPOSITORY = CompositeRepository(EnvRepository(), RepositorySecret(_SECRETS_PATH))


def env(name: str, default: Any | None = None) -> Any | None:
    """Read a raw config value from repositories.

    Priority: OS environment > secrets directory. Returns ``default`` if missing.
    """
    if name in _REPOSITORY:
        return _REPOSITORY[name]
    return default


def get_bool(name: str, default: bool = False) -> bool:
    """Read a boolean env var with tolerant parsing.

    Accepts: 1/0, true/false, yes/no, y/n, on/off (case-insensitive).
    Falls back to ``default`` for missing or unrecognized values.
    """
    raw = env(name, default=None)
    if raw is None:
        return default
    value = str(raw).strip().lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    return default


def get_int(name: str, default: int = 0) -> int:
    return int(env(name, default=default))


def get_float(name: str, default: float = 0.0) -> float:
    return float(env(name, default=default))


def get_list(
    name: str,
    *,
    item_cast: Callable[[str], T] | type[T] | None = None,
    default: Sequence[T] | None = None,
    separator: str = ",",
) -> list[T]:
    """Read a delimited list env var with optional item casting.

    - Supports raw lists/tuples (already split) or delimited strings.
    - Trims whitespace around items; skips empty items.
    - ``item_cast`` can be a callable or a ``type`` (e.g., ``int``).
    - Returns ``default`` (copied into a ``list``) or ``[]`` if missing.
    """
    raw = env(name, default=None)
    if raw is None:
        return list(default) if default is not None else []
    if isinstance(raw, list | tuple):
        items = (str(item).strip() for item in raw)
    else:
        items = (item.strip() for item in str(raw).split(separator))
    caster: Callable[[str], T]
    if item_cast is None:

        def _identity(x: str) -> T:
            return cast(T, x)

        caster = _identity
    else:
        caster = cast(Callable[[str], T], item_cast)
    return [caster(item) for item in items if item]


__all__ = ["env", "get_bool", "get_int", "get_float", "get_list"]
