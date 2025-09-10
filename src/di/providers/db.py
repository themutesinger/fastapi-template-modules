from __future__ import annotations

from dishka import module, provide, singleton
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from configs.env import env


@module
def db_module():
    database_url = env("DATABASE_URL", default="sqlite+aiosqlite:///test.db")
    engine = create_async_engine(database_url)

    @singleton
    def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    return provide(get_sessionmaker)
