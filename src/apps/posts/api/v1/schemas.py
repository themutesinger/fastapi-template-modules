from __future__ import annotations

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    body: str
    userId: int


class PostRead(BaseModel):
    id: int | None = None
    title: str
    body: str
    userId: int


