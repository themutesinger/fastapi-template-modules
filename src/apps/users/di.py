from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from di.providers.security import PBKDF2PasswordHasher
from infra.db.transaction import TransactionManager

from .repository import UserRepository
from .service import RegisterUserUseCase, GetUserUseCase


class UsersProvider(Provider):
    @provide(scope=Scope.APP)
    def password_hasher(self) -> PBKDF2PasswordHasher:
        return PBKDF2PasswordHasher()

    @provide(scope=Scope.REQUEST)
    def repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def register_usecase(self, repo: UserRepository, password_hasher: PBKDF2PasswordHasher, tx: TransactionManager) -> RegisterUserUseCase:
        return RegisterUserUseCase(repo, password_hasher, tx)

    @provide(scope=Scope.REQUEST)
    def get_user_usecase(self, repo: UserRepository) -> GetUserUseCase:
        return GetUserUseCase(repo)


di = UsersProvider()
