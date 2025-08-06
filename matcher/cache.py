# matcher/cache.py
import hashlib
import json
import time
from uuid import UUID

import redis
from django.conf import settings

r = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


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
    key = f"match_result:{answers_hash}"
    data = {
        "pokemon_id": (
            str(pokemon_id) if isinstance(pokemon_id, UUID) else pokemon_id
        ),  # Proper UUID conversion
        "score": score,
        "timestamp": time.time(),
    }
    r.setex(key, ttl, json.dumps(data))
    print(f"DEBUG: Cached match result for hash {answers_hash}")


def get_cached_match(answers_hash: str):
    """Get cached match result"""
    key = f"match_result:{answers_hash}"
    cached = r.get(key)
    if cached:
        print(f"DEBUG: Found cached match for hash {answers_hash}")
        return json.loads(cached)
    return None
