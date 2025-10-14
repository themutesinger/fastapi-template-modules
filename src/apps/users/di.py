from __future__ import annotations

from dishka import singleton
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from configs import Settings
from di.providers.security import PasswordHasher, PBKDF2PasswordHasher

from .repository import UserRepository
from .service import UserService





