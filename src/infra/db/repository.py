from __future__ import annotations

from typing import Generic, Iterable, Optional, Type, TypeVar, Sequence

from sqlalchemy import select, func
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

    async def filter_by(self, **kwargs) -> Iterable[ModelT]:
        result = await self._session.execute(select(self._model).filter_by(**kwargs))
        return list(result.scalars().all())

    async def exists(self, **kwargs) -> bool:
        stmt = select(func.count()).select_from(self._model).filter_by(**kwargs)
        result = await self._session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def paginate(
        self,
        *,
        page: int,
        page_size: int,
        where: Optional[object] = None,
        order_by: Optional[Sequence[object]] = None,
        sort: Optional[str] = None,
    ) -> tuple[list[ModelT], int]:
        if page < 1:
            page = 1
        offset = (page - 1) * page_size
        base = select(self._model)
        if where is not None:
            base = base.where(where)
        # Parse sort like "field:asc,other:desc" using model columns
        if sort:
            cols: list[object] = []
            for part in sort.split(","):
                part = part.strip()
                if not part:
                    continue
                if ":" in part:
                    name, direction = part.split(":", 1)
                else:
                    name, direction = part, "asc"
                col = getattr(self._model, name, None)
                if col is None:
                    continue
                cols.append(col.asc() if direction.lower() == "asc" else col.desc())
            if cols:
                base = base.order_by(*cols)
        elif order_by:
            base = base.order_by(*order_by)

        data_result = await self._session.execute(base.offset(offset).limit(page_size))
        items = list(data_result.scalars().all())

        count_stmt = select(func.count()).select_from(self._model)
        if where is not None:
            count_stmt = count_stmt.where(where)
        count_result = await self._session.execute(count_stmt)
        total = int(count_result.scalar_one() or 0)
        return items, total


