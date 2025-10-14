from __future__ import annotations

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from configs import Settings
from infra.db import make_engine, make_session_factory



class DBProvider(Provider):
    """Provides database engine and sessions for dependency injection."""

    @provide(scope=Scope.APP)
    async def engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        """Create and yield an async SQLAlchemy engine."""
        url = settings.get_database_url()
        pool_size = settings.DB.POOL_SIZE if getattr(settings, "DB", None) else None
        max_overflow = settings.DB.MAX_OVERFLOW if getattr(settings, "DB", None) else None

        engine = make_engine(
            url,
            echo=settings.DEBUG,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """Return a configured async session factory."""
        return make_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """Provide a scoped async session for request lifetime."""
        async with session_factory() as session:
            yield session