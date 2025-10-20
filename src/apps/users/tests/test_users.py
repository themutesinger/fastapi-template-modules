
import pytest
from typing import Any

from fastapi import status
from httpx import AsyncClient, ASGITransport

from apps.users.service import RegisterUserUseCase, GetUserUseCase


class FakeRepo:
    def __init__(self) -> None:
        self._by_email: dict[str, Any] = {}
        self._by_id: dict[int, Any] = {}
        self._id = 0

    async def get_by_email(self, email: str):
        return self._by_email.get(email)

    async def add(self, *, email: str, hashed_password: str):
        self._id += 1
        user = type("User", (), {"id": self._id, "email": email, "hashed_password": hashed_password, "is_active": True})
        self._by_email[email] = user
        self._by_id[self._id] = user
        return user

    async def get_by_id(self, user_id: int):
        return self._by_id.get(user_id)


class FakeHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"


@pytest.mark.asyncio
async def test_usecases_register_and_get():
    repo = FakeRepo()
    reg = RegisterUserUseCase(repo, FakeHasher())
    get = GetUserUseCase(repo)

    user = await reg.execute(email="u@example.com", password="p")
    assert user.email == "u@example.com"
    fetched = await get.execute(user.id)
    assert fetched.id == user.id


@pytest.mark.asyncio
async def test_api_users_create_and_get(monkeypatch):
    from dishka import Provider, Scope, provide
    from dishka import make_async_container
    from dishka.integrations.fastapi import FastapiProvider

    fake_repo = FakeRepo()
    fake_hasher = FakeHasher()

    class TestProvider(Provider):
        @provide(scope=Scope.APP)
        def repository(self) -> Any:
            return fake_repo

        @provide(scope=Scope.APP)
        def password_hasher(self) -> Any:
            return fake_hasher

        @provide(scope=Scope.REQUEST)
        def register_usecase(self) -> RegisterUserUseCase:
            return RegisterUserUseCase(fake_repo, fake_hasher)

        @provide(scope=Scope.REQUEST)
        def get_user_usecase(self) -> GetUserUseCase:
            return GetUserUseCase(fake_repo)

    container = make_async_container(FastapiProvider(), TestProvider())

    from presentations.api.app import create_app

    app = create_app(container=container)
    transport = ASGITransport(app=app)
    headers = {"Accept-Language": "en", "Content-Type": "application/json"}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        res = await client.post("/api/v1/users/", json={"email": "t@example.com", "password": "pass12345"})
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        user_id = data["id"]

        res2 = await client.get(f"/api/v1/users/{user_id}")
        assert res2.status_code == status.HTTP_200_OK
        data2 = res2.json()
        assert data2["email"] == "t@example.com"


