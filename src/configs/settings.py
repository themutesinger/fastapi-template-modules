
import os
from typing import Any, List, Optional
from urllib.parse import quote_plus

from pydantic import Field, field_validator
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


class Settings(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        secrets_dir=["/run/secrets", "/etc/secrets"],
    )

    # Core app
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool
    PORT: int
    LOG_LEVEL: str

    # Database (flat)
    DB_DRIVER: str = "postgresql+asyncpg"
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_OPTIONS: Optional[str] = None

    DB_POOL_SIZE: Optional[int] = None
    DB_MAX_OVERFLOW: Optional[int] = None

    DB_PGBOUNCER_ENABLED: bool = False
    DB_PGBOUNCER_DSN: Optional[str] = None

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 60

    # Cookies
    COOKIE_NAME: str = "session"
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "Lax"
    COOKIE_DOMAIN: Optional[str] = None
    COOKIE_PATH: str = "/"

    # CORS / Allowed hosts
    CORS_ORIGINS: List[str] = Field(default_factory=list)
    ALLOWED_HOSTS: List[str] = Field(default_factory=list)

    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # Sentry / Observability
    SENTRY_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENV: Optional[str] = None  # defaults to APP_ENV if not set
    SENTRY_RELEASE: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.0
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.0
    SENTRY_SEND_PII: bool = False

    # S3 / Storage
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_SECURE: bool = True
    S3_USE_PATH_STYLE: bool = True

    # Pagination defaults
    PAGINATION_DEFAULT_PAGE: int = 1
    PAGINATION_DEFAULT_PAGE_SIZE: int = 20
    PAGINATION_MAX_PAGE_SIZE: int = 100

    # i18n / Localization
    I18N_ENABLED: bool = True
    I18N_DEFAULT_LOCALE: str = "en"
    I18N_FALLBACK_LOCALE: str = "en"
    I18N_DOMAIN: str = "messages"
    I18N_LOCALES_DIR: str = "src/infra/i18n/locales"

    # External APIs
    JSONPLACEHOLDER_BASE_URL: str = "https://jsonplaceholder.typicode.com"

    @field_validator("CORS_ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def _parse_list(cls, value: Any) -> List[str]:
        return split_comma_separated(value)

    def build_database_url(self) -> Optional[str]:
        if self.DB_PGBOUNCER_ENABLED and self.DB_PGBOUNCER_DSN:
            return self.DB_PGBOUNCER_DSN
        if not all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME, self.DB_PORT]):
            return None
        safe_user = quote_plus(self.DB_USER or "")
        safe_pass = quote_plus(self.DB_PASSWORD or "")
        base = f"{self.DB_DRIVER}://{safe_user}:{safe_pass}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        if self.DB_OPTIONS:
            sep = "?" if "?" not in base else "&"
            return f"{base}{sep}{self.DB_OPTIONS}"
        return base

    def get_database_url(self) -> str:
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        built = self.build_database_url()
        if built:
            return built
        return self.DATABASE_URL or ""
