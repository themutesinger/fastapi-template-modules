from __future__ import annotations

import asyncio
from typing import Dict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from dishka.integrations.fastapi import FromDishka
from infra.redis.client import RedisClient


READINESS_TIMEOUT_SECONDS = 1.5


async def check_db(engine: AsyncEngine) -> str:
    try:
        async with asyncio.timeout(READINESS_TIMEOUT_SECONDS):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "down"


async def check_redis(redis_client: RedisClient) -> str:
    ok = await redis_client.ping()
    return "ok" if ok else "down"


async def build_readiness(engine: AsyncEngine, redis_client: RedisClient | None = None) -> Dict[str, str]:
    # Run checks concurrently when redis_client provided
    if redis_client is None:
        db_status = await check_db(engine)
        return {"db": db_status}
    db_task = asyncio.create_task(check_db(engine))
    redis_task = asyncio.create_task(check_redis(redis_client))
    db_status, redis_status = await asyncio.gather(db_task, redis_task)
    return {"db": db_status, "redis": redis_status}


