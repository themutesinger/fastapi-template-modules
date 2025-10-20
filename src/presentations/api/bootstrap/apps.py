from __future__ import annotations

from typing import Iterable, List

from apps.appconfig import AppConfig, discover_app_paths, load_app_configs as _load_app_configs


def load_app_configs(paths: Iterable[str] | None = None) -> List[AppConfig]:
    """Discover and instantiate AppConfig objects."""
    paths = list(paths) if paths is not None else discover_app_paths()
    return _load_app_configs(paths)
