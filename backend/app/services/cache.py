import json
import logging
from typing import Any

from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(settings.redis_url, decode_responses=True)
    return _pool


def _client() -> Redis:
    return Redis(connection_pool=_get_pool())


async def cache_get(key: str) -> Any | None:
    val = await _client().get(key)
    if val is None:
        logger.debug("cache miss: %s", key)
        return None
    logger.debug("cache hit: %s", key)
    return json.loads(val)


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    await _client().set(
        key,
        json.dumps(value, default=str),
        ex=ttl or settings.cache_ttl_seconds,
    )


async def ping() -> bool:
    return await _client().ping()
