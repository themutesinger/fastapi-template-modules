from __future__ import annotations

from typing import Generic, List, Optional, Sequence, TypeVar

from pydantic import BaseModel


class ErrorItem(BaseModel):
    code: str
    detail: str
    attr: Optional[str] = None


class ErrorResponse(BaseModel):
    message: str
    errors: List[ErrorItem]


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: Sequence[T]


