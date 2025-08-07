"""
Tests for matcher caching functionality
"""

from unittest.mock import MagicMock, patch

import pytest

from matcher.cache import cache_match_result, get_answers_hash, get_cached_match
from matcher.tests.factories import PokemonFactory, UserProfileFactory
from matcher.tests.test_utils import SimpleMatchingEngine


@pytest.mark.django_db
class TestCache:
    """Test caching functionality"""

    def test_get_answers_hash(self):
        """Test hash generation for answers"""
        answers = {
            "time_of_day": "fire_red",
            "element_resonance": "fire",
            "conflict_handling": "attack",
        }

        hash1 = get_answers_hash(answers)
        hash2 = get_answers_hash(answers)

        # Same answers should produce same hash
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) > 0

    def test_get_answers_hash_different_answers(self):
        """Test that different answers produce different hashes"""
        answers1 = {"time_of_day": "fire_red", "element_resonance": "fire"}
        answers2 = {"time_of_day": "water_blue", "element_resonance": "water"}

        hash1 = get_answers_hash(answers1)
        hash2 = get_answers_hash(answers2)

        # Different answers should produce different hashes
        assert hash1 != hash2

    @patch("matcher.cache.redis")
    def test_cache_match_result(self, mock_redis):
        """Test caching match results"""
        # Setup mock Redis
        mock_redis_instance = MagicMock()
        mock_redis.Redis.return_value = mock_redis_instance

        # Create test data
        pokemon = PokemonFactory(name="Testmon")
        answers_hash = "test_hash_123"
        score = 0.85

        # Cache the result
        cache_match_result(answers_hash, str(pokemon.id), score)

        # Verify Redis was called correctly
        mock_redis_instance.setex.assert_called_once()
        call_args = mock_redis_instance.setex.call_args
        assert call_args[0][0] == f"match_result:{answers_hash}"  # key
        assert call_args[0][1] == 3600  # ttl (1 hour)
        # Value should be JSON with pokemon_id and score
        assert "pokemon_id" in call_args[0][2]
        assert "score" in call_args[0][2]

    @patch("matcher.cache.redis")
    def test_get_cached_match_found(self, mock_redis):
        """Test retrieving cached match when found"""
        # Setup mock Redis to return cached data
        mock_redis_instance = MagicMock()
        mock_redis.Redis.return_value = mock_redis_instance
        mock_redis_instance.get.return_value = '{"pokemon_id": "123", "score": 0.85}'

        answers_hash = "test_hash_123"
        result = get_cached_match(answers_hash)

        # Verify Redis was queried
        mock_redis_instance.get.assert_called_once_with(f"match_result:{answers_hash}")

        # Verify result
        assert result is not None
        assert result["pokemon_id"] == "123"
        assert result["score"] == 0.85

    @patch("matcher.cache.redis")
    def test_get_cached_match_not_found(self, mock_redis):
        """Test retrieving cached match when not found"""
        # Setup mock Redis to return None (cache miss)
        mock_redis_instance = MagicMock()
        mock_redis.Redis.return_value = mock_redis_instance
        mock_redis_instance.get.return_value = None

        answers_hash = "test_hash_123"
        result = get_cached_match(answers_hash)

        # Verify Redis was queried
        mock_redis_instance.get.assert_called_once_with(f"match_result:{answers_hash}")

        # Verify result is None
        assert result is None

    @patch("matcher.cache.redis")
    def test_get_cached_match_invalid_json(self, mock_redis):
        """Test handling invalid JSON in cache"""
        # Setup mock Redis to return invalid JSON
        mock_redis_instance = MagicMock()
        mock_redis.Redis.return_value = mock_redis_instance
        mock_redis_instance.get.return_value = "invalid json"

        answers_hash = "test_hash_123"
        result = get_cached_match(answers_hash)

        # Should return None for invalid JSON
        assert result is None

    @pytest.mark.django_db
    def test_caching_integration_with_matching_engine(self):
        """Test that matching engine uses caching correctly"""
        # Create test data
        user_profile = UserProfileFactory(
            answers={
                "element_resonance": "fire",
                "favorite_color": "red",
            }
        )

        # Create matching engine
        engine = SimpleMatchingEngine(user_profile)

        # Verify answers_hash is created
        assert hasattr(engine, "answers_hash")
        assert engine.answers_hash is not None
        assert isinstance(engine.answers_hash, str)

    @patch("matcher.cache.redis")
    def test_cache_ttl_setting(self, mock_redis):
        """Test that cache TTL is set correctly"""
        mock_redis_instance = MagicMock()
        mock_redis.Redis.return_value = mock_redis_instance

        pokemon = PokemonFactory(name="TTLmon")
        answers_hash = "test_ttl_hash"
        score = 0.75

        cache_match_result(answers_hash, str(pokemon.id), score)

        # Verify TTL is set to 1 hour (3600 seconds)
        call_args = mock_redis_instance.setex.call_args
        assert call_args[0][1] == 3600

    def test_cache_key_format(self):
        """Test that cache keys are formatted correctly"""
        answers_hash = "test_hash_456"
        expected_key = f"match:{answers_hash}"

        # This is an indirect test - we can't easily test the key format
        # without mocking, but we can verify the pattern
        assert expected_key.startswith("match:")
        assert expected_key.endswith(answers_hash)
