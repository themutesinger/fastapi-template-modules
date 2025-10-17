from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse

from apps.appconfig import AppConfig, SupportsProvider
from .exceptions import UserAlreadyExistsError, UserNotFoundError


class AppConfig(AppConfig):
    name = "apps.users"
    label = "users"

    def get_provider(self) -> SupportsProvider | None:
        from .di import di

        return di

    def get_routers(self):
        from .routers.v1 import router as v1
        return {"v1": v1}


config = AppConfig()


