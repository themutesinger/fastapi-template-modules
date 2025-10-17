from __future__ import annotations

from typing import Generic, Iterable, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class BaseRepository(Generic[ModelT]):
    """Generic repository for SQLAlchemy models using a shared AsyncSession.

    - No commit/rollback; managed by UnitOfWork/TransactionManager
    - Provides common CRUD helpers
    """

    def __init__(self, session: AsyncSession, model: Type[ModelT]):
        self._session = session
        self._model = model

    async def add(self, instance: ModelT) -> ModelT:
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def get_by_id(self, id_: int) -> Optional[ModelT]:
        return await self._session.get(self._model, id_)

    async def list_all(self) -> Iterable[ModelT]:
        result = await self._session.execute(select(self._model))
        return list(result.scalars().all())

    async def delete(self, instance: ModelT) -> None:
        await self._session.delete(instance)


