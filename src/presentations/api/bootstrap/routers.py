from __future__ import annotations

from typing import Iterable, Mapping

from fastapi import APIRouter, FastAPI

from apps.appconfig import AppConfig


def collect_versioned_routers(configs: Iterable[AppConfig]) -> Mapping[str, APIRouter]:
    """Aggregate routers exposed by feature apps grouped by API version."""
    version_to_router: dict[str, APIRouter] = {}
    for cfg in configs:
        routers = cfg.get_routers()
        if not routers:
            continue
        for version, router in routers.items():
            prefix = f"/api/{version}"
            version_router = version_to_router.setdefault(version, APIRouter(prefix=prefix))
            if router.prefix and router.prefix.startswith("/api/"):
                version_router.include_router(router)
            else:
                version_router.include_router(router, prefix="")
    return version_to_router


def include_versioned_routers(app: FastAPI, configs: Iterable[AppConfig]) -> None:
    for version, router in sorted(collect_versioned_routers(configs).items()):
        app.include_router(router)
