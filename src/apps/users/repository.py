from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, text

from .models import User
from infra.db.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository based on BaseRepository with shared AsyncSession."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def add(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        return await super().add(user)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await super().get_by_id(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> Iterable[User]:
        return await super().list_all()

    async def ping_db(self, session: AsyncSession) -> bool:
        try:
            await session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False






