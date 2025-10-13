from __future__ import annotations

from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import APIRouter, HTTPException, status

from apps.users.schemas import UserCreate, UserRead
from .service import UserService


router = APIRouter(prefix="/users", tags=["users"])
router.route_class = DishkaRoute


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: FromDishka[UserService],
):
    try:
        user = await service.register(email=payload.email, password=payload.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User exists")
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, service: FromDishka[UserService]):
    user = await service.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return UserRead.model_validate(user)


