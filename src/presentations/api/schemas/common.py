
from typing import Generic, List, Optional, Sequence, TypeVar
from fastapi import Request

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

    @classmethod
    def from_request(
        cls,
        request: Request,
        *,
        results: Sequence[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        def url_for(p: int) -> str:
            q = dict(request.query_params)
            q["page"] = str(p)
            return str(request.url.replace_query_params(**q))

        next_url = url_for(page + 1) if page < total_pages else None
        prev_url = url_for(page - 1) if page > 1 and total_pages > 0 else None
        return cls(count=total, next=next_url, previous=prev_url, results=list(results))


class PaginationParams(BaseModel):
    page: int
    page_size: int
    sort: Optional[str] = None  # format: "field:asc,other:desc"


