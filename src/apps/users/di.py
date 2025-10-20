from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infra.db.transaction import TransactionManager
from infra.security import PasswordHasher

from .repository import UserRepository
from .service import RegisterUserUseCase, GetUserUseCase, ListUsersUseCase


class UsersProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def register_usecase(self, repo: UserRepository, password_hasher: PasswordHasher, tx: TransactionManager) -> RegisterUserUseCase:
        return RegisterUserUseCase(repo, password_hasher, tx)

    @provide(scope=Scope.REQUEST)
    def get_user_usecase(self, repo: UserRepository) -> GetUserUseCase:
        return GetUserUseCase(repo)

    @provide(scope=Scope.REQUEST)
    def list_users_usecase(self, repo: UserRepository) -> ListUsersUseCase:
        return ListUsersUseCase(repo)


di = UsersProvider()
