from __future__ import annotations

from .env import env, get_bool, get_int, get_list

# Core app settings
APP_NAME: str = env("APP_NAME", default="FastAPI Template")
# Prefer APP_ENV (as in docker-compose), fallback to ENV for compatibility
APP_ENV: str = env("APP_ENV", default=env("ENV", default="development"))
ENV: str = APP_ENV  # keep alias for code expecting ENV
DEBUG: bool = get_bool("DEBUG", default=False)
PORT: int = get_int("PORT", default=8000)
LOG_LEVEL: str = env("LOG_LEVEL", default="INFO")

# Networking / CORS
CORS_ORIGINS: list[str] = get_list("CORS_ORIGINS", default=[])
ALLOWED_HOSTS: list[str] = get_list("ALLOWED_HOSTS", default=["localhost"])

__all__ = []
