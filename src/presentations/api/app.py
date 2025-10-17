from fastapi import APIRouter, FastAPI

from apps.appconfig import load_app_configs, discover_app_paths

from di.container import setup_di
from configs.logging import configure_logging
from infra.observability.bootstrap import init_observability
from infra.logging import TraceIdFilter  # noqa: F401  # ensure import path is resolvable for dictConfig
from presentations.api.middlewares.trace import trace_id_middleware
from presentations.api.middlewares.locale import locale_middleware
from presentations.api.exception_handlers import get_exception_handlers
from presentations.api.health import build_readiness
from dishka.integrations.fastapi import FromDishka
from sqlalchemy.ext.asyncio import AsyncEngine
from infra.redis.client import RedisClient
from infra.storage.client import StorageClient
from fastapi import status as http_status


def create_app(container=None) -> FastAPI:
    app = FastAPI()
    # Initialize logging early using settings.LOG_LEVEL
    try:
        from configs import settings as app_settings
        # Initialize observability (logging + sentry)
        init_observability(app_settings)
    except Exception:
        # Fallback to default INFO if settings are not ready yet
        configure_logging("INFO")

    setup_di(app, container=container)

    # Load routers by version from AppConfig
    version_to_router: dict[str, APIRouter] = {}
    for cfg in load_app_configs(discover_app_paths()):
        routers = cfg.get_routers()
        if routers:
            for version, r in routers.items():
                if version not in version_to_router:
                    version_to_router[version] = APIRouter(prefix=f"/api/{version}")
                version_to_router[version].include_router(r)
        handlers = getattr(cfg, "get_exception_handlers", None)
        if handlers is not None:
            mapping = handlers()
            if mapping:
                for exc_type, handler in mapping.items():
                    app.add_exception_handler(exc_type, handler)
    for version, router in sorted(version_to_router.items()):
        app.include_router(router)

    # Middleware: Trace/Request ID
    app.middleware("http")(trace_id_middleware)
    # Middleware: Locale (Accept-Language)
    app.middleware("http")(locale_middleware)

    # Global exception handlers (422 for validation, consistent error shape)
    for exc_type, handler in get_exception_handlers().items():
        app.add_exception_handler(exc_type, handler)

    @app.get("/health/live", status_code=200)
    async def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def health_ready(
        engine: FromDishka[AsyncEngine],
        redis_client: FromDishka[RedisClient],
        storage: FromDishka[StorageClient],
    ):
        components = await build_readiness(engine, redis_client, storage)
        overall_ok = all(v == "ok" for v in components.values())
        status_code = http_status.HTTP_200_OK if overall_ok else http_status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "ok" if overall_ok else "degraded", "components": components}

    return app


app = create_app()


