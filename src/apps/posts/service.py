from __future__ import annotations

from typing import List

from infra.httpx.jsonplaceholder import JSONPlaceholderClient, Post


class ListPostsUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self) -> List[Post]:
        return await self._client.list_posts()


class GetPostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, post_id: str) -> Post:
        return await self._client.get_post(post_id)


class CreatePostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, *, title: str, body: str, user_id: int) -> Post:
        return await self._client.create_post(Post(title=title, body=body, userId=user_id))


class UpdatePostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, post_id: str, *, title: str, body: str, user_id: int) -> Post:
        return await self._client.update_post(post_id, Post(id=int(post_id), title=title, body=body, userId=user_id))


class DeletePostUseCase:
    def __init__(self, client: JSONPlaceholderClient) -> None:
        self._client = client

    async def execute(self, post_id: str) -> None:
        await self._client.delete_post(post_id)


