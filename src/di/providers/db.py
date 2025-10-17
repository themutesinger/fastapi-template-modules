from __future__ import annotations

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from configs import Settings
from infra.db import make_engine, make_session_factory
from infra.db.transaction import TransactionManager



class DBProvider(Provider):
    """Provides database engine and sessions for dependency injection."""

    @provide(scope=Scope.APP)
    async def engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        """Create and yield an async SQLAlchemy engine."""
        url = settings.get_database_url()
        pool_size = settings.DB_POOL_SIZE
        max_overflow = settings.DB_MAX_OVERFLOW

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

    @provide(scope=Scope.REQUEST)
    def transaction_manager(self, session: AsyncSession) -> TransactionManager:
        """Provide a request-scoped transaction manager based on the current session."""
        return TransactionManager(session)