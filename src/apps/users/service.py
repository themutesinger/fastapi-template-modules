from __future__ import annotations

from typing import Optional

from di.providers.security import PasswordHasher

from .models import User
from .repository import UserRepository
from apps.users.views.schemas import UserCreate


class UserService:
    def __init__(self, repo: UserRepository, hasher: PasswordHasher) -> None:
        self._repo = repo
        self._hasher = hasher

    async def register(self, data: UserCreate) -> User:
        existing = await self._repo.get_by_email(data.email)
        if existing is not None:
            raise ValueError("User already exists")
        password_hash = self._hasher.hash(data.password)
        return await self._repo.add(email=data.email, hashed_password=password_hash)

    async def get(self, user_id: int) -> Optional[User]:
        return await self._repo.get_by_id(user_id)






