from __future__ import annotations

import os
from typing import Any, List, Optional
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def split_comma_separated(value: Any) -> List[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        items = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        items = [str(item) for item in value]
    else:
        items = [str(value)]
    return [item.strip() for item in items if item and item.strip()]


class AppSettings(BaseSettings):
    """Base settings with env and Docker/K8s secrets."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        secrets_dir=["/run/secrets", "/etc/secrets"],
    )


class DatabaseSettings(BaseModel):
    DRIVER: str = "postgresql+asyncpg"
    HOST: Optional[str] = None
    PORT: Optional[int] = None
    USER: Optional[str] = None
    PASSWORD: Optional[str] = None
    NAME: Optional[str] = None
    OPTIONS: Optional[str] = None

    POOL_SIZE: Optional[int] = None
    MAX_OVERFLOW: Optional[int] = None

    USE_PGBOUNCER: bool = Field(default=False, alias="DB_PGBOUNCER_ENABLED")
    PGBOUNCER_DSN: Optional[str] = Field(default=None, alias="DB_PGBOUNCER_DSN")

    def build_database_url(self) -> Optional[str]:
        """Build a full DSN string from fields."""
        if self.USE_PGBOUNCER and self.PGBOUNCER_DSN:
            return self.PGBOUNCER_DSN
        if not all([self.HOST, self.USER, self.PASSWORD, self.NAME, self.PORT]):
            return None
        safe_user = quote_plus(self.USER or "")
        safe_pass = quote_plus(self.PASSWORD or "")
        base = f"{self.DRIVER}://{safe_user}:{safe_pass}@{self.HOST}:{self.PORT}/{self.NAME}"
        if self.OPTIONS:
            sep = "?" if "?" not in base else "&"
            return f"{base}{sep}{self.OPTIONS}"
        return base


class AuthSettings(BaseModel):
    SECRET_KEY: str = Field(alias="JWT_SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRES_MINUTES: int = Field(
        default=60, alias="JWT_ACCESS_TOKEN_EXPIRES_MINUTES"
    )


class CookieSettings(BaseModel):
    NAME: str = Field(default="session", alias="COOKIE_NAME")
    SECURE: bool = Field(default=True, alias="COOKIE_SECURE")
    SAMESITE: str = Field(default="Lax", alias="COOKIE_SAMESITE")
    DOMAIN: Optional[str] = Field(default=None, alias="COOKIE_DOMAIN")
    PATH: str = Field(default="/", alias="COOKIE_PATH")


class CorsSettings(BaseModel):
    ORIGINS: List[str] = Field(default_factory=list, alias="CORS_ORIGINS")
    ALLOWED_HOSTS: List[str] = Field(default_factory=list, alias="ALLOWED_HOSTS")

    @field_validator("ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def _parse_list(cls, value: Any) -> List[str]:
        return split_comma_separated(value)


class Settings(AppSettings):
    """Main application configuration."""

    # Core app
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool
    PORT: int
    LOG_LEVEL: str

    # Sub-configs
    DB: DatabaseSettings
    AUTH: AuthSettings
    COOKIES: CookieSettings
    CORS: CorsSettings

    DATABASE_URL: Optional[str] = None

    def get_database_url(self) -> str:
        """Single source of truth for DB URL."""
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        if self.DB is not None:
            built = self.DB.build_database_url()
            if built:
                return built
        return self.DATABASE_URL or ""
