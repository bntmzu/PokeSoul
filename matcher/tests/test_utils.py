"""
Test utilities for matcher tests to avoid code duplication
"""

from unittest.mock import Mock, patch

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APIRequestFactory

from core.global_exception_handler import custom_exception_handler
from matcher.dataclasses import MatchProfile
from matcher.exceptions import MatchingFailed
from matcher.matching_engine import MatchingEngine


class SimpleMatchingEngine(MatchingEngine):
    """Simplified matching engine for testing with custom profile creation"""

    def __init__(self, user_profile):
        # Don't call super().__init__() to avoid preference extraction
        self.user_profile = user_profile
        # Create a simple match profile based on answers
        self.match_profile = self._create_simple_profile()
        # Add missing answers_hash attribute for caching
        self.answers_hash = "test_hash"

    def _create_simple_profile(self):
        """Create a simple match profile from answers"""
        types = []
        color = None
        habitat = None
        ability_keywords = []
        personality_tags = []
        stat_preferences = {}

        # Extract types from answers
        if "element_resonance" in self.user_profile.answers:
            types.append(self.user_profile.answers["element_resonance"])

        # Extract color
        if "favorite_color" in self.user_profile.answers:
            color = self.user_profile.answers["favorite_color"]

        # Extract habitat
        if "place_you_belong" in self.user_profile.answers:
            habitat = self.user_profile.answers["place_you_belong"]

        # Extract stat preferences
        if "conflict_handling" in self.user_profile.answers:
            stat = self.user_profile.answers["conflict_handling"]
            stat_preferences[stat] = 1

        return MatchProfile(
            types=types,
            color=color,
            habitat=habitat,
            ability_keywords=ability_keywords,
            personality_tags=personality_tags,
            stat_preferences=stat_preferences,
        )


class TestCustomExceptionHandler:
    """Test custom exception handler functionality"""

    def test_custom_exception_handler_logs_matcher_exceptions(self):
        """Test that custom exception handler logs matcher-specific exceptions"""
        factory = APIRequestFactory()
        request = factory.post("/api/match/")
        request.user = None  # Set user to None for anonymous access

        # Create context with request
        context = {"request": request}

        # Test with NotFound exception (replaces NoSuitablePokemon)
        exception = NotFound("No suitable Pokemon found")

        with patch("core.global_exception_handler.logger") as mock_logger:
            custom_exception_handler(exception, context)

            # Verify logger was called with warning level for DRF exceptions
            mock_logger.warning.assert_called_once()
            log_message = mock_logger.warning.call_args[0][0]

            # Verify log message contains expected information
            assert "API Exception" in log_message
            assert "NotFound" in log_message
            assert "anonymous" in log_message  # No authenticated user
            assert "/api/match/" in log_message

    def test_custom_exception_handler_ignores_other_exceptions(self):
        """Test that custom exception handler doesn't log non-matcher exceptions"""
        factory = APIRequestFactory()
        request = factory.post("/api/match/")
        request.user = None  # Set user to None for anonymous access
        context = {"request": request}

        # Test with a regular exception
        exception = ValueError("Test error")

        with patch("core.global_exception_handler.logger") as mock_logger:
            custom_exception_handler(exception, context)

            # Verify logger was called with warning level for non-custom exceptions
            mock_logger.warning.assert_called_once()

    def test_custom_exception_handler_with_authenticated_user(self):
        """Test custom exception handler with authenticated user"""
        factory = APIRequestFactory()
        request = factory.post("/api/match/")

        # Mock authenticated user
        mock_user = Mock()
        mock_user.id = 123
        request.user = mock_user

        context = {"request": request}
        exception = ValidationError("User profile has no answers")

        with patch("core.global_exception_handler.logger") as mock_logger:
            custom_exception_handler(exception, context)

            # Verify logger was called with warning level for DRF exceptions
            mock_logger.warning.assert_called_once()
            log_message = mock_logger.warning.call_args[0][0]
            assert "User: 123" in log_message

    def test_custom_exception_handler_without_request(self):
        """Test custom exception handler when request is not available"""
        context = {"request": None}
        exception = MatchingFailed()

        with patch("core.global_exception_handler.logger") as mock_logger:
            custom_exception_handler(exception, context)

            # Verify logger was called with error level for custom exceptions
            mock_logger.error.assert_called_once()
            log_message = mock_logger.error.call_args[0][0]
            assert "User: unknown" in log_message
            assert "Path: unknown" in log_message
