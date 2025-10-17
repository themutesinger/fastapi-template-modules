from __future__ import annotations

import asyncio
from typing import Dict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


READINESS_TIMEOUT_SECONDS = 1.5


async def check_db(engine: AsyncEngine) -> str:
    try:
        async with asyncio.timeout(READINESS_TIMEOUT_SECONDS):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "down"


async def build_readiness(engine: AsyncEngine) -> Dict[str, str]:
    # Extend here: run checks concurrently for other deps (redis, broker, s3, http integrations)
    db_status = await check_db(engine)
    return {"db": db_status}


