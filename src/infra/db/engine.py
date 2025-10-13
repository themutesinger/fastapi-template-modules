from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from configs import Settings


def make_engine(settings: Settings) -> AsyncEngine:
    """Create AsyncEngine with sane defaults.

    - pool_pre_ping=True to avoid stale connections
    - echo based on debug flag
    """
    url = settings.get_database_url()
    pool_size = getattr(settings.db, "pool_size", None) if getattr(settings, "db", None) else None
    max_overflow = getattr(settings.db, "max_overflow", None) if getattr(settings, "db", None) else None
    kwargs: dict[str, object] = {
        "pool_pre_ping": True,
        "echo": settings.debug,
    }
    if pool_size is not None:
        kwargs["pool_size"] = pool_size
    if max_overflow is not None:
        kwargs["max_overflow"] = max_overflow
    return create_async_engine(url, **kwargs)
