from __future__ import annotations

from typing import List

from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import APIRouter, status

from apps.posts.api.v1.schemas import PostCreate, PostRead
from apps.posts.service import ListPostsUseCase, GetPostUseCase, CreatePostUseCase, UpdatePostUseCase, DeletePostUseCase
from presentations.api.schemas.common import PaginatedResponse


router = APIRouter(prefix="/posts", tags=["posts"])
router.route_class = DishkaRoute


@router.get("/", response_model=List[PostRead])
async def list_posts(usecase: FromDishka[ListPostsUseCase]):
    items = await usecase.execute()
    return items


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreate, usecase: FromDishka[CreatePostUseCase]):
    return await usecase.execute(title=payload.title, body=payload.body, user_id=payload.userId)


@router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: str, usecase: FromDishka[GetPostUseCase]):
    return await usecase.execute(post_id)


@router.put("/{post_id}", response_model=PostRead)
async def update_post(post_id: str, payload: PostCreate, usecase: FromDishka[UpdatePostUseCase]):
    return await usecase.execute(post_id, title=payload.title, body=payload.body, user_id=payload.userId)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: str, usecase: FromDishka[DeletePostUseCase]):
    await usecase.execute(post_id)
    return None


