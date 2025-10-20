
from typing import Iterable

from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter, FastAPI, status as http_status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine

from apps.appconfig import discover_app_paths, load_app_configs
from configs.logging import configure_logging
from di.container import setup_di
from infra.logging import TraceIdFilter  # noqa: F401  # ensure dictConfig can import the filter
from infra.observability.bootstrap import init_observability
from infra.redis.client import RedisClient
from infra.storage.client import StorageClient
from presentations.api.exception_handlers import get_exception_handlers
from presentations.api.health import build_readiness
from presentations.api.middlewares.locale import locale_middleware
from presentations.api.middlewares.trace import trace_id_middleware


def _bootstrap_environment() -> str:
    """Initialize logging, observability, and i18n; return the app title."""
    default_title = "FastAPI Application"

    try:
        from configs import settings as app_settings
    except Exception:
        configure_logging("INFO")
        return default_title

    # Логирование должно быть инициализировано до observability
    configure_logging(app_settings.LOG_LEVEL)
    init_observability(app_settings)

    # Настройка i18n не относится к observability, но тоже часть инфраструктуры
    try:
        from infra.i18n import configure as configure_i18n

        configure_i18n(
            enabled=app_settings.I18N_ENABLED,
            default_locale=app_settings.I18N_DEFAULT_LOCALE,
            fallback_locale=app_settings.I18N_FALLBACK_LOCALE,
            domain=app_settings.I18N_DOMAIN,
            locales_dir=app_settings.I18N_LOCALES_DIR,
        )
    except Exception:
        # Ошибки i18n не критичны — просто логируем и продолжаем
        import logging
        logging.getLogger(__name__).warning("Failed to initialize i18n", exc_info=True)

    return getattr(app_settings, "APP_NAME", default_title)


def _collect_versioned_routers(configs: Iterable) -> dict[str, APIRouter]:
    """Aggregate routers exposed by application modules grouped by API version."""
    version_to_router: dict[str, APIRouter] = {}
    for cfg in configs:
        routers = getattr(cfg, "get_routers", lambda: None)()
        if not routers:
            continue
        for version, router in routers.items():
            # Избегаем двойного /api/v1/api/v1 при уже заданных префиксах
            prefix = f"/api/{version}"
            version_router = version_to_router.setdefault(version, APIRouter(prefix=prefix))
            if not router.prefix.startswith("/api/"):
                version_router.include_router(router, prefix="")
            else:
                version_router.include_router(router)
    return version_to_router


def _register_module_exception_handlers(app: FastAPI, configs: Iterable) -> None:
    """Attach exception handlers declared by app modules."""
    for cfg in configs:
        handlers_factory = getattr(cfg, "get_exception_handlers", None)
        if not handlers_factory:
            continue
        handlers = handlers_factory() or {}
        for exc_type, handler in handlers.items():
            app.add_exception_handler(exc_type, handler)


def _register_global_exception_handlers(app: FastAPI) -> None:
    """Attach global (framework-level) exception handlers."""
    for exc_type, handler in get_exception_handlers().items():
        app.add_exception_handler(exc_type, handler)


def _register_middlewares(app: FastAPI) -> None:
    """Register global HTTP middlewares in the correct order."""
    # FastAPI применяет middleware в обратном порядке регистрации,
    # поэтому locale_middleware добавляем ПЕРЕД trace_id_middleware
    app.middleware("http")(locale_middleware)
    app.middleware("http")(trace_id_middleware)


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

        if all(v == "ok" for v in components.values()):
            status_text, status_code = "ok", http_status.HTTP_200_OK
        elif any(v == "ok" for v in components.values()):
            status_text, status_code = "degraded", http_status.HTTP_200_OK
        else:
            status_text, status_code = "unavailable", http_status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(
            status_code=status_code,
            content={"status": status_text, "components": components},
        )


def _include_versioned_routers(app: FastAPI, configs: Iterable) -> None:
    """Attach all versioned routers discovered from modules."""
    for version, router in sorted(_collect_versioned_routers(configs).items()):
        app.include_router(router)


def build_app(container=None) -> FastAPI:
    """Create and configure the FastAPI application instance."""
    title = _bootstrap_environment()

    app_configs = list(load_app_configs(discover_app_paths()))

    app = FastAPI(
        title=title,
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    setup_di(app, container=container)
    _register_middlewares(app)

    # Сначала регистрируем модульные (узкие) хендлеры, затем глобальные (общие)
    _register_module_exception_handlers(app, app_configs)
    _register_global_exception_handlers(app)

    _include_versioned_routers(app, app_configs)
    _register_health_endpoints(app)

    return app
