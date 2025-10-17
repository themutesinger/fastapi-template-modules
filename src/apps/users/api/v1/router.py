from __future__ import annotations

from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import APIRouter, status

from apps.users.api.v1.schemas import UserCreate, UserRead
from apps.users.service import RegisterUserUseCase, GetUserUseCase


router = APIRouter(prefix="/users", tags=["users"])
router.route_class = DishkaRoute


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    usecase: FromDishka[RegisterUserUseCase],
):
    user = await usecase.execute(email=payload.email, password=payload.password)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, usecase: FromDishka[GetUserUseCase]):
    user = await usecase.execute(user_id)
    return UserRead.model_validate(user)


