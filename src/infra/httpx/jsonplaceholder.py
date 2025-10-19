from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from infra.httpx.base.base import BaseApiClient


class Post(BaseModel):
    id: Optional[int] = Field(None, description="ID of the post")
    title: str
    body: str
    userId: int


class JSONPlaceholderClient(BaseApiClient):
    async def list_posts(self) -> List[Post]:
        data = await self.request("GET", "/posts")
        return [Post.model_validate(item) for item in data]

    async def create_post(self, post: Post) -> Post:
        data = await self.request("POST", "/posts", json=post.model_dump(exclude_none=True))
        return Post.model_validate(data)

    async def get_post(self, post_id: str) -> Post:
        data = await self.request("GET", f"/posts/{post_id}")
        return Post.model_validate(data)

    async def update_post(self, post_id: str, post: Post) -> Post:
        data = await self.request("PUT", f"/posts/{post_id}", json=post.model_dump(exclude_none=True))
        return Post.model_validate(data)

    async def delete_post(self, post_id: str) -> None:
        await self.request("DELETE", f"/posts/{post_id}")
        return None


