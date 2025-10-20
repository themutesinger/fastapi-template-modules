from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from infra.httpx.base.base import BaseApiClient


class _PostSchema(BaseModel):
    id: Optional[int] = Field(None, description="ID of the post")
    title: str
    body: str
    userId: int


class JSONPlaceholderClient(BaseApiClient):
    async def list_posts(self) -> List[Dict[str, Any]]:
        data = await self.request("GET", "/posts")
        return [_PostSchema.model_validate(item).model_dump() for item in data]

    async def create_post(self, *, title: str, body: str, user_id: int) -> Dict[str, Any]:
        payload = {"title": title, "body": body, "userId": user_id}
        data = await self.request("POST", "/posts", json=payload)
        return _PostSchema.model_validate(data).model_dump()

    async def get_post(self, post_id: int) -> Dict[str, Any]:
        data = await self.request("GET", f"/posts/{post_id}")
        return _PostSchema.model_validate(data).model_dump()

    async def update_post(self, post_id: int, *, title: str, body: str, user_id: int) -> Dict[str, Any]:
        payload = {"id": post_id, "title": title, "body": body, "userId": user_id}
        data = await self.request("PUT", f"/posts/{post_id}", json=payload)
        return _PostSchema.model_validate(data).model_dump()

    async def delete_post(self, post_id: int) -> None:
        await self.request("DELETE", f"/posts/{post_id}")
        return None


__all__ = ["JSONPlaceholderClient"]
