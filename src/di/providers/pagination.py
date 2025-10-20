
from typing import AsyncIterable

from dishka import Provider, Scope, provide
from fastapi import Request

from configs import Settings
from presentations.api.schemas.common import PaginationParams


class PaginationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def pagination_params(self, request: Request, settings: Settings) -> PaginationParams:
        qp = request.query_params
        default_page = settings.PAGINATION_DEFAULT_PAGE
        default_page_size = settings.PAGINATION_DEFAULT_PAGE_SIZE
        max_page_size = settings.PAGINATION_MAX_PAGE_SIZE

        try:
            page = int(qp.get("page", default_page))
        except Exception:
            page = default_page
        if page < 1:
            page = 1

        try:
            page_size = int(qp.get("page_size", default_page_size))
        except Exception:
            page_size = default_page_size
        if page_size < 1:
            page_size = default_page_size
        if page_size > max_page_size:
            page_size = max_page_size

        sort = qp.get("sort")
        return PaginationParams(page=page, page_size=page_size, sort=sort)


