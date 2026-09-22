import os
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "")

_redis_client = None
_redis_available = False

async def init_redis():
    """Initialize Redis connection pool. Fails silently if Redis is unavailable."""
    global _redis_client, _redis_available
    if not REDIS_URL:
        logger.info("REDIS_URL not set, using in-memory fallback")
        return
    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
        await _redis_client.ping()
        _redis_available = True
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis unavailable, using in-memory fallback: {e}")
        _redis_available = False

async def close_redis():
    global _redis_client, _redis_available
    if _redis_client:
        await _redis_client.close()
        _redis_available = False
        logger.info("Redis connection closed")

async def get_redis():
    """FastAPI dependency: returns Redis client or None."""
    if _redis_available:
        return _redis_client
    return None

# === Rate Limiting ===

async def check_rate_limit(tenant_id: str, limit_per_minute: int = 60) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    if not _redis_available:
        return True  # Fail-open in dev
    try:
        key = f"rate:tenant:{tenant_id}:minute"
        current = await _redis_client.incr(key)
        if current == 1:
            await _redis_client.expire(key, 60)
        return current <= limit_per_minute
    except Exception:
        return True  # Fail-open on error

# === Simple Cache ===

# Bounded in-memory cache with LRU eviction
_MEMORY_CACHE_MAX_SIZE = 10_000
_memory_cache: OrderedDict = OrderedDict()

async def cache_get(key: str) -> str | None:
    if _redis_available:
        try:
            return await _redis_client.get(key)
        except Exception:
            pass
    value = _memory_cache.get(key)
    if value is not None:
        _memory_cache.move_to_end(key)  # LRU: mark as recently used
    return value

async def cache_set(key: str, value: str, ttl: int = 3600) -> None:
    if _redis_available:
        try:
            await _redis_client.setex(key, ttl, value)
            return
        except Exception:
            pass
    _memory_cache[key] = value
    _memory_cache.move_to_end(key)
    while len(_memory_cache) > _MEMORY_CACHE_MAX_SIZE:
        _memory_cache.popitem(last=False)  # Evict oldest
