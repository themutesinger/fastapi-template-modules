from __future__ import annotations

from contextlib import asynccontextmanager

from dishka import Container, make_async_container
from dishka.integrations.fastapi import DishkaRoute, FastapiProvider, setup_dishka
from fastapi import FastAPI

from . import ConfigProvider, DBProvider, RedisProvider, StorageProvider
from apps.appconfig import load_app_configs, discover_app_paths


def build_container() -> Container:
    """Assemble DI container from base providers and AppConfig providers."""
    providers = [ConfigProvider(), DBProvider(), RedisProvider(), StorageProvider(), FastapiProvider()]

    app_configs = load_app_configs(discover_app_paths())
    for cfg in app_configs:
        provider = cfg.get_provider()
        if provider is not None:
            providers.append(provider)

    return make_async_container(*providers)


def setup_di(app: FastAPI, container: Container | None = None) -> Container:
    """Attach Dishka container to FastAPI app.

    If an external container is provided (e.g., in tests), it will be used as-is.
    Otherwise, a default container will be built.
    """
    if container is None:
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
