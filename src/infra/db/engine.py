
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def make_engine(
    url: str,
    *,
    echo: bool,
    pool_size: int | None = None,
    max_overflow: int | None = None,
) -> AsyncEngine:
    """Create AsyncEngine with sane defaults and optional pool tuning."""
    kwargs: dict[str, object] = {
        "pool_pre_ping": True,
        "echo": echo,
    }
    if pool_size is not None:
        kwargs["pool_size"] = pool_size
    if max_overflow is not None:
        kwargs["max_overflow"] = max_overflow
    return create_async_engine(url, **kwargs)
