from __future__ import annotations

from apps.appconfig import AppConfig as BaseAppConfig, SupportsProvider


class AppConfig(BaseAppConfig):
    name = "apps.posts"
    label = "posts"

    def get_provider(self) -> SupportsProvider | None:
        from .di import di

        return di

    def get_routers(self):
        from .api.v1.router import router as v1
        return {"v1": v1}


config = AppConfig()


