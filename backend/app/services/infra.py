from __future__ import annotations

import os
import time
from collections import defaultdict

import redis


REDIS_URL = os.getenv("REDIS_URL")
_memory_bucket: dict[tuple[str, str], list[float]] = defaultdict(list)
_redis_client: redis.Redis | None = None


def redis_client() -> redis.Redis | None:
    global _redis_client
    if not REDIS_URL:
        return None
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=0.2, socket_timeout=0.2)
    return _redis_client


def redis_status() -> dict:
    client = redis_client()
    if client is None:
        return {"mode": "memory", "connected": False, "url": None}
    try:
        client.ping()
        return {"mode": "redis", "connected": True, "url": REDIS_URL}
    except redis.RedisError as exc:
        return {"mode": "memory_fallback", "connected": False, "error": exc.__class__.__name__}


def enforce_distributed_rate_limit(user_id: str, tool_name: str, max_calls: int = 8, window_seconds: int = 60) -> bool:
    client = redis_client()
    if client is not None:
        try:
            key = f"rate_limit:{user_id}:{tool_name}:{int(time.time() // window_seconds)}"
            current = client.incr(key)
            if current == 1:
                client.expire(key, window_seconds + 5)
            return current <= max_calls
        except redis.RedisError:
            pass

    key = (user_id, tool_name)
    cutoff = time.time() - window_seconds
    _memory_bucket[key] = [stamp for stamp in _memory_bucket[key] if stamp > cutoff]
    if len(_memory_bucket[key]) >= max_calls:
        return False
    _memory_bucket[key].append(time.time())
    return True
