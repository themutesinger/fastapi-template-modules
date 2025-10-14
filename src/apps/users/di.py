from __future__ import annotations

from dishka import singleton
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from configs import Settings
from di.providers.security import PasswordHasher, PBKDF2PasswordHasher

from .repository import UserRepository
from .service import UserService


@singleton
def get_user_repository(sessionmaker: async_sessionmaker[AsyncSession]) -> UserRepository:
    return UserRepository(sessionmaker)


@singleton
def get_user_service(repo: UserRepository, settings: Settings) -> UserService:
    salt_source = f"{settings.app_name}:{settings.app_env}:{settings.port}:{settings.log_level}"
    hasher: PasswordHasher = PBKDF2PasswordHasher(secret_salt=salt_source)
    return UserService(repo, hasher)

di = [get_user_repository, get_user_service]




