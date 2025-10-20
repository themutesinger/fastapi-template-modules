
from dishka.integrations.fastapi import FromDishka
from fastapi import FastAPI, status as http_status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine

from di.container import setup_di
from infra.logging import TraceIdFilter  # noqa: F401  # ensure dictConfig can import the filter
from infra.redis.client import RedisClient
from infra.storage.client import StorageClient
from presentations.api.health import build_readiness
from presentations.api.bootstrap import (
    include_versioned_routers,
    load_app_configs,
    load_settings,
    register_exception_handlers,
    register_middlewares,
)


def _register_health_endpoints(app: FastAPI) -> None:
    """Expose liveness and readiness probes for infra monitoring."""

    @app.get("/health/live", status_code=http_status.HTTP_200_OK)
    async def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def health_ready(
        engine: FromDishka[AsyncEngine],
        redis_client: FromDishka[RedisClient],
        storage: FromDishka[StorageClient],
    ):
        components = await build_readiness(engine, redis_client, storage)

        if all(status == "ok" for status in components.values()):
            status_text, status_code = "ok", http_status.HTTP_200_OK
        elif any(status == "ok" for status in components.values()):
            status_text, status_code = "degraded", http_status.HTTP_200_OK
        else:
            status_text, status_code = "unavailable", http_status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(
            status_code=status_code,
            content={"status": status_text, "components": components},
        )

def build_app(container=None) -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = load_settings()
    app_title = settings.APP_NAME if settings else "FastAPI Application"
    app_configs = load_app_configs()

    app = FastAPI(
        title=app_title,
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    setup_di(app, container=container)
    register_middlewares(app, settings)
    register_exception_handlers(app, app_configs)
    include_versioned_routers(app, app_configs)
    _register_health_endpoints(app)

    return app
