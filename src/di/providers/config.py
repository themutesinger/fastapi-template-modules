from __future__ import annotations

from dishka import Provider, Scope, provide

from configs import Settings


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()




