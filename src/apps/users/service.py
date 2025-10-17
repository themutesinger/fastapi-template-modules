from __future__ import annotations

from typing import Optional

from di.providers.security import PBKDF2PasswordHasher
from infra.db.transaction import TransactionManager

from .models import User
from .repository import UserRepository
from .exceptions import UserAlreadyExistsError, UserNotFoundError


class RegisterUserUseCase:
    def __init__(self, repo: UserRepository, hasher: PBKDF2PasswordHasher, tx: TransactionManager) -> None:
        self._repo = repo
        self._hasher = hasher
        self._tx = tx

    async def execute(self, *, email: str, password: str) -> User:
        async with self._tx:
            existing = await self._repo.get_by_email(email)
            if existing is not None:
                raise UserAlreadyExistsError("User already exists")
            password_hash = self._hasher.hash(password)
            user = await self._repo.add(email=email, hashed_password=password_hash)
            await self._tx.flush()
            return user


class GetUserUseCase:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def execute(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        return user


class ListUsersUseCase:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def execute(self, *, page: int, page_size: int):
        return await self._repo.paginate(page=page, page_size=page_size)






