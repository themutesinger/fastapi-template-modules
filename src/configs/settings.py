from __future__ import annotations

from .env import env, get_bool, get_int, get_list

# Core app settings
APP_NAME: str = env("APP_NAME", default="FastAPI Template")
ENV: str = env("ENV", default="development")
DEBUG: bool = get_bool("DEBUG", default=False)
PORT: int = get_int("PORT", default=8000)
LOG_LEVEL: str = env("LOG_LEVEL", default="INFO")

# Networking / CORS
CORS_ORIGINS: list[str] = get_list("CORS_ORIGINS", default=[])
ALLOWED_HOSTS: list[str] = get_list("ALLOWED_HOSTS", default=["localhost"])

__all__ = [
    "APP_NAME",
    "ENV",
    "DEBUG",
    "PORT",
    "LOG_LEVEL",
    "CORS_ORIGINS",
    "ALLOWED_HOSTS",
]

