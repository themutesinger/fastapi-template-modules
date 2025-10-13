from __future__ import annotations

import os
from typing import Any, Iterable, List

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


def split_comma_separated(value: Any) -> List[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        items = value.split(",")
    elif isinstance(value, Iterable):
        items = [str(item) for item in value]
    else:
        items = [str(value)]
    return [item.strip() for item in items if item and item.strip()]


class AppSettings(BaseSettings):
    """Base settings: env variables first; optional Docker/K8s secrets at /run/secrets."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        secrets_dir="/run/secrets",
    )


 
