from __future__ import annotations

from contextlib import asynccontextmanager

from dishka import Container, make_async_container
from dishka.integrations.fastapi import DishkaRoute, FastapiProvider, setup_dishka
from fastapi import FastAPI

from . import ConfigProvider, DBProvider


def build_container() -> Container:
    """Manually register base providers and module providers here.

    Add app providers explicitly when apps are implemented, e.g.:
        from apps.users.di import di as users_di
        from apps.auth.di import di as auth_di
        return make_async_container(ConfigProvider(), DBProvider(), FastapiProvider(), users_di, auth_di)
    """
    # Import app providers explicitly here
    try:
        from apps.users.di import di as users_di
    except Exception:
        users_di = None

    providers = [
        ConfigProvider(),
        DBProvider(),
        FastapiProvider(),
    ]
    if users_di is not None:
        providers.append(users_di)
    return make_async_container(*providers)


def setup_di(app: FastAPI) -> Container:
    container = build_container()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            await container.close()

    app.router.route_class = DishkaRoute
    app.router.lifespan_context = lifespan
    setup_dishka(container=container, app=app)
    return container
