from __future__ import annotations

import os
from typing import Any


class EnvRepository:
    """Simple repository that reads from process environment."""

    def __contains__(self, key: str) -> bool:
        return key in os.environ

    def __getitem__(self, key: str) -> str:
        return os.environ[key]


class RepositorySecret:
    """Filesystem-backed repository similar to python-decouple example.

    Reads files from a directory (e.g., Docker/K8s secrets) and exposes them as
    uppercase keys -> file contents (as text, unmodified).
    """

    def __init__(self, source: str):
        self.data: dict[str, str] = {}

        if not os.path.isdir(source):
            return

        for entry in os.listdir(source):
            path = os.path.join(source, entry)
            if os.path.isdir(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.data[entry.upper()] = f.read()
            except OSError:
                # Silently skip unreadable files
                continue

    def __contains__(self, key: str) -> bool:
        return key in self.data or key in os.environ

    def __getitem__(self, key: str) -> str:
        if key in os.environ:
            return os.environ[key]
        return self.data[key]


class CompositeRepository:
    """Chain multiple repositories with first-hit wins policy."""

    def __init__(self, *repositories: Any):
        self.repositories = repositories

    def __contains__(self, key: str) -> bool:
        return any(key in repo for repo in self.repositories)

    def __getitem__(self, key: str) -> str:
        for repo in self.repositories:
            if key in repo:
                return repo[key]
        raise KeyError(key)
