import json

import redis
from django.conf import settings

# Initialize Redis connection
# Expect REDIS_HOST and REDIS_PORT in your settings.py or .env
r = redis.Redis(
    host=getattr(settings, "REDIS_HOST"),
    port=getattr(settings, "REDIS_PORT"),
    db=0,
    decode_responses=True,  # Get string instead of bytes
)


def get_pokemon_from_cache(name: str) -> dict | None:
    """
    Retrieve a cached Pokémon response from Redis by name.
    """
    key = f"pokemon:{name.lower()}"
    cached: str | None = r.get(key)
    return json.loads(cached) if cached else None


def set_pokemon_to_cache(name: str, data: dict, ttl: int = 86400) -> None:
    """
    Store a Pokémon response in Redis cache for a given TTL (default 24h).
    """
    key = f"pokemon:{name.lower()}"
    r.setex(key, ttl, json.dumps(data))


def delete_pokemon_from_cache(name: str) -> None:
    """
    Optional: Remove a specific Pokémon from cache (for future updates).
    """
    key = f"pokemon:{name.lower()}"
    r.delete(key)
