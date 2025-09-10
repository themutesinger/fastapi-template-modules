from __future__ import annotations

from dataclasses import dataclass

from dishka import module, provide, singleton

from configs import settings as conf_settings


@dataclass
class Settings:
    app_name: str = conf_settings.APP_NAME
    app_env: str = conf_settings.APP_ENV
    debug: bool = conf_settings.DEBUG
    port: int = conf_settings.PORT
    log_level: str = conf_settings.LOG_LEVEL
    cors_origins: list[str] = conf_settings.CORS_ORIGINS
    allowed_hosts: list[str] = conf_settings.ALLOWED_HOSTS


@module
def settings_module():
    @singleton
    def get_settings() -> Settings:
        return Settings()

    return provide(get_settings)
