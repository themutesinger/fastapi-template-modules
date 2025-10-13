from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, text

from .models import User


class UserRepository:
    """User repository using SQLAlchemy async sessionmaker."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    async def add(self, email: str, hashed_password: str) -> User:
        async with self._sessionmaker() as session:
            user = User(email=email, hashed_password=hashed_password)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            await session.commit()
            return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        async with self._sessionmaker() as session:
            return await session.get(User, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self._sessionmaker() as session:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def list_all(self) -> Iterable[User]:
        async with self._sessionmaker() as session:
            result = await session.execute(select(User))
            return list(result.scalars().all())

    async def ping_db(self, session: AsyncSession) -> bool:
        try:
            await session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False






