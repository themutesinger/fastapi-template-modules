from __future__ import annotations

from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import APIRouter, status, Query, Request

from apps.users.api.v1.schemas import UserCreate, UserRead
from apps.users.service import RegisterUserUseCase, GetUserUseCase, ListUsersUseCase
from apps.users.models import User
from presentations.api.schemas.common import PaginatedResponse, PaginationParams


router = APIRouter(prefix="/users", tags=["users"])
router.route_class = DishkaRoute


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    usecase: FromDishka[RegisterUserUseCase],
):
    user = await usecase.execute(email=payload.email, password=payload.password)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, usecase: FromDishka[GetUserUseCase]):
    user = await usecase.execute(user_id)
    return user


@router.get("/", response_model=PaginatedResponse[UserRead])
async def list_users(
    request: Request,
    pagination: FromDishka[PaginationParams],
    usecase: FromDishka[ListUsersUseCase] = None,
):
    items, total = await usecase.execute(page=pagination.page, page_size=pagination.page_size)
    return PaginatedResponse[UserRead].from_request(
        request,
        results=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )

