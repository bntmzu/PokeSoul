# matcher/cache.py
import hashlib
import json
import logging
import time
from uuid import UUID

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def get_redis_connection():
    """Get Redis connection with fallback to default values"""
    try:
        return redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            decode_responses=True,
        )
    except Exception:
        # Return None if Redis is not available
        return None


def get_answers_hash(answers: dict) -> str:
    """Create unique hash of answers for caching"""
    # Sort answers for consistent hash
    sorted_answers = sorted(answers.items())
    answers_str = json.dumps(sorted_answers, sort_keys=True)
    return hashlib.sha256(answers_str.encode()).hexdigest()


def cache_match_result(
    answers_hash: str, pokemon_id: str | UUID, score: float, ttl: int = 3600
):
    """Cache match result for 1 hour"""
    r = get_redis_connection()
    if r is None:
        return  # Skip caching if Redis is not available

    key = f"match_result:{answers_hash}"
    data = {
        "pokemon_id": (
            str(pokemon_id) if isinstance(pokemon_id, UUID) else pokemon_id
        ),  # Proper UUID conversion
        "score": score,
        "timestamp": time.time(),
    }
    r.setex(key, ttl, json.dumps(data))
    logger.debug(f"Cached match result for hash {answers_hash[:8]}... (truncated)")


def get_cached_match(answers_hash: str):
    """Get cached match result"""
    r = get_redis_connection()
    if r is None:
        return None  # Return None if Redis is not available

    key = f"match_result:{answers_hash}"
    cached = r.get(key)
    if cached:
        logger.debug(f"Found cached match for hash {answers_hash[:8]}... (truncated)")
        try:
            return json.loads(cached)
        except (json.JSONDecodeError, TypeError):
            # Return None for invalid JSON
            return None
    return None
