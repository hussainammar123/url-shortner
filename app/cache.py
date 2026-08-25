import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

try:
    import redis
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    # Ping to check availability
    redis_client.ping()
    is_redis_available = True
    logger.info("Connected to Redis successfully.")
except Exception as e:
    redis_client = None
    is_redis_available = False
    logger.warning(f"Redis unavailable ({e}). Using in-memory fallback cache.")

# Fallback in-memory cache
_memory_cache = {}
_memory_clicks = {}

class CacheService:
    @staticmethod
    def get_url(short_code: str) -> Optional[str]:
        if is_redis_available and redis_client:
            try:
                return redis_client.get(f"url:{short_code}")
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        return _memory_cache.get(f"url:{short_code}")

    @staticmethod
    def set_url(short_code: str, original_url: str, ttl: int = 86400):
        if is_redis_available and redis_client:
            try:
                redis_client.setex(f"url:{short_code}", ttl, original_url)
                return
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        _memory_cache[f"url:{short_code}"] = original_url

    @staticmethod
    def increment_click(short_code: str) -> int:
        if is_redis_available and redis_client:
            try:
                return redis_client.incr(f"clicks:{short_code}")
            except Exception as e:
                logger.error(f"Redis incr error: {e}")
        current = _memory_clicks.get(short_code, 0) + 1
        _memory_clicks[short_code] = current
        return current

    @staticmethod
    def invalidate_url(short_code: str):
        if is_redis_available and redis_client:
            try:
                redis_client.delete(f"url:{short_code}")
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        _memory_cache.pop(f"url:{short_code}", None)
