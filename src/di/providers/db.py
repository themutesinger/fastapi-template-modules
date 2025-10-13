from __future__ import annotations

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from configs import Settings
from infra.db import make_engine, make_session_factory


class DBProvider(Provider):
    @provide(scope=Scope.APP)
    async def engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        url = settings.get_database_url()
        pool_size = getattr(settings.db, "pool_size", None) if getattr(settings, "db", None) else None
        max_overflow = getattr(settings.db, "max_overflow", None) if getattr(settings, "db", None) else None

        engine = make_engine(url, echo=settings.debug, pool_size=pool_size, max_overflow=max_overflow)
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return make_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def session(self, session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with session_factory() as s:
            yield s




