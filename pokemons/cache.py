import json

import redis
from django.conf import settings


def get_redis_connection():
    """Get Redis connection with fallback to default values"""
    try:
        return redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=0,
            decode_responses=True,
        )
    except Exception:
        # Return None if Redis is not available
        return None


def get_pokemon_from_cache(name: str) -> dict | None:
    """
    Retrieve a cached Pokémon response from Redis by name.
    """
    r = get_redis_connection()
    if r is None:
        return None  # Return None if Redis is not available

    key = f"pokemon:{name.lower()}"
    cached: str | None = r.get(key)
    return json.loads(cached) if cached else None


def set_pokemon_to_cache(name: str, data: dict, ttl: int = 86400) -> None:
    """
    Store a Pokémon response in Redis cache for a given TTL (default 24h).
    """
    r = get_redis_connection()
    if r is None:
        return  # Skip caching if Redis is not available

    key = f"pokemon:{name.lower()}"
    r.setex(key, ttl, json.dumps(data))


def delete_pokemon_from_cache(name: str) -> None:
    """
    Optional: Remove a specific Pokémon from cache (for future updates).
    """
    r = get_redis_connection()
    if r is None:
        return  # Skip if Redis is not available

    key = f"pokemon:{name.lower()}"
    r.delete(key)
