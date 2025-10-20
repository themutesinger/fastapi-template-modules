
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
        exists = await storage.bucket_exists()
        return "ok" if exists else "down"
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

