from __future__ import annotations

import asyncio
from typing import Dict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from dishka.integrations.fastapi import FromDishka
from infra.redis.client import RedisClient
from infra.storage.client import StorageClient


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


async def check_storage(storage: StorageClient) -> str:
    try:
        # head bucket via exists on a dummy key pattern is expensive; instead try list with max-keys=0 (not available easily here)
        # As a light check, just return ok if client could initialize resource (already ensured); real checks can be added later
        return "ok"
    except Exception:
        return "down"


async def build_readiness(
    engine: AsyncEngine,
    redis_client: RedisClient | None = None,
    storage: StorageClient | None = None,
) -> Dict[str, str]:
    # Run checks concurrently when redis_client provided
    if redis_client is None:
        db_status = await check_db(engine)
        return {"db": db_status}

    tasks = [asyncio.create_task(check_db(engine))]
    names = ["db"]
    if redis_client is not None:
        tasks.append(asyncio.create_task(check_redis(redis_client)))
        names.append("redis")
    if storage is not None:
        tasks.append(asyncio.create_task(check_storage(storage)))
        names.append("storage")
    results = await asyncio.gather(*tasks)
    return {name: status for name, status in zip(names, results)}


