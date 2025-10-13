from __future__ import annotations

from typing import Any, Optional

import os
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, field_validator

from pydantic import Field, field_validator

from .base import AppSettings, split_comma_separated


class DatabaseSettings(BaseModel):
    driver: str = "postgresql+asyncpg"
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    options: Optional[str] = None  # e.g. "sslmode=disable"

    pool_size: Optional[int] = None
    max_overflow: Optional[int] = None

    use_pgbouncer: bool = Field(default=False, alias="DB_PGBOUNCER_ENABLED")
    pgbouncer_dsn: Optional[str] = Field(default=None, alias="DB_PGBOUNCER_DSN")

    def build_database_url(self) -> Optional[str]:
        if self.use_pgbouncer and self.pgbouncer_dsn:
            return self.pgbouncer_dsn
        if not all([self.host, self.user, self.password, self.name, self.port]):
            return None
        safe_user = quote_plus(self.user or "")
        safe_pass = quote_plus(self.password or "")
        base = f"{self.driver}://{safe_user}:{safe_pass}@{self.host}:{self.port}/{self.name}"
        if self.options:
            sep = "?" if "?" not in base else "&"
            return f"{base}{sep}{self.options}"
        return base


class Settings(AppSettings):
    """Project configuration values."""

    # Core app
    app_name: str
    app_env: str
    debug: bool
    port: int
    log_level: str

    # CORS / hosts
    cors_origins: list[str] = Field(default_factory=list)
    allowed_hosts: list[str] = Field(default_factory=list)

    # Database (either database_url or structured db fields)
    database_url: str
    db: Optional[DatabaseSettings] = Field(default=None)

    # Auth
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expires_minutes: int

    # Cookies
    cookie_name: str
    cookie_secure: bool
    cookie_samesite: str
    cookie_domain: Optional[str] = None
    cookie_path: str

    @field_validator("cors_origins", "allowed_hosts", mode="before")
    @classmethod
    def _parse_list(cls, value: Any) -> list[str]:
        return split_comma_separated(value)

    def get_database_url(self) -> str:
        """Single source of truth for DB URL.

        Priority:
        1) env DATABASE_URL
        2) explicit db.url or builder from structured fields
        3) fallback to top-level database_url
        """
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        if self.db is not None:
            built = self.db.build_database_url()
            if built:
                return built
        return self.database_url

settings = Settings()
