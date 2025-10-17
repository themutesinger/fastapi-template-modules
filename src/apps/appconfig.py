from __future__ import annotations

from typing import Any, Iterable, Optional, Protocol, Mapping, Callable, Type, Dict
import pkgutil


class SupportsProvider(Protocol):
    """Protocol representing a Dishka Provider-like object.

    We keep it structural to avoid importing dishka types here.
    """

    # Marker protocol; no methods required for container assembly
    ...


class AppConfig:
    """Base AppConfig contract for feature apps.

    Apps should provide a module `apps.<name>.apps` with `AppConfig` class.
    Methods can return None if the app does not expose a router or provider.
    """

    name: str = ""
    label: str = ""

    def get_provider(self) -> Optional[SupportsProvider]:  # pragma: no cover - thin wrapper
        return None

    def get_router(self) -> Optional[Any]:  # FastAPI APIRouter, but avoid import here
        return None

    def get_routers(self) -> Optional[Dict[str, Any]]:
        """Optional map of version -> APIRouter.

        Default: try legacy get_router(); else attempt discovery under `api.v*`.
        """
        legacy = self.get_router()
        if legacy is not None:
            return {"v1": legacy}
        # Attempt simple discovery: import apps.<name>.api.v1.router if exists
        try:
            import importlib
            mod = importlib.import_module(f"{self.name}.api.v1.router")
            router = getattr(mod, "router", None)
            if router is not None:
                return {"v1": router}
        except Exception:
            pass
        return None
    def get_exception_handlers(self) -> Optional[Mapping[Type[BaseException], Callable[..., Any]]]:
        """Optional mapping of exception type to handler callables.

        Handlers must be compatible with FastAPI's exception handlers signature.
        """
        return None


def _import_app_config(app_path: str) -> Optional[AppConfig]:
    """Import and instantiate AppConfig from `<app_path>.apps`.

    Looks for attribute `AppConfig` (class) or `config` (instance).
    Returns None if not found or failed to import.
    """

    import importlib

    try:
        mod = importlib.import_module(f"{app_path}.apps")
    except Exception:
        return None

    config_obj: Optional[AppConfig] = None
    if hasattr(mod, "config"):
        maybe = getattr(mod, "config")
        if isinstance(maybe, AppConfig) or (hasattr(maybe, "get_provider") and hasattr(maybe, "get_router")):
            config_obj = maybe  # type: ignore[assignment]
    if config_obj is None and hasattr(mod, "AppConfig"):
        cls = getattr(mod, "AppConfig")
        try:
            config_obj = cls()  # type: ignore[call-arg]
        except Exception:
            return None
    return config_obj


def load_app_configs(app_paths: Iterable[str]) -> list[AppConfig]:
    configs: list[AppConfig] = []
    for app in app_paths:
        cfg = _import_app_config(app)
        if cfg is not None:
            configs.append(cfg)
    return configs


def discover_app_paths(package: str = "apps") -> list[str]:
    """Return dotted import paths for first-level packages under `apps`.

    Only includes subpackages that import successfully and have an `apps` module with AppConfig.
    """
    import importlib

    try:
        pkg = importlib.import_module(package)
    except Exception:
        return []

    discovered: list[str] = []
    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__, prefix=f"{package}."):
        if not ispkg:
            continue
        # accept if AppConfig import works
        cfg = _import_app_config(name)
        if cfg is not None:
            discovered.append(name)
    return discovered


