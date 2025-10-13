from __future__ import annotations

from typing import Any, Optional

from pydantic import Field, field_validator

from .base import AppSettings, split_comma_separated


class Settings(AppSettings):
    """Project configuration values."""

    app_name: str = "FastAPI Template"
    app_env: str = "development"
    debug: bool = False
    port: int = 8000
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=list)
    allowed_hosts: list[str] = Field(default_factory=lambda: ["localhost"])
    database_url: str = "sqlite+aiosqlite:///test.db"
    jwt_secret_key: str = "change-me-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 30
    cookie_name: str = "session"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cookie_domain: Optional[str] = None
    cookie_path: str = "/"

    @field_validator("cors_origins", "allowed_hosts", mode="before")
    @classmethod
    def _parse_list(cls, value: Any) -> list[str]:
        return split_comma_separated(value)

settings = Settings()
