"""
Global exception handler for PokeSoul project
"""

import logging

from django.conf import settings
from django.utils import timezone
from rest_framework.views import exception_handler

from matcher.exceptions import (
    MatchingFailed,
)
from pokemons.exceptions import (
    InvalidPokemonData,
    PokemonAPIUnavailable,
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Global exception handler for API responses with detailed logging"""

    # Get request information
    request = context.get("request")
    user_id = getattr(request.user, "id", "anonymous") if request else "unknown"
    path = request.path if request else "unknown"
    view_name = context.get("view", {}).__class__.__name__

    # Define all custom exceptions for special handling
    custom_exceptions = (
        # Matcher exceptions
        MatchingFailed,
        # Pokemon exceptions
        PokemonAPIUnavailable,
        InvalidPokemonData,
    )

    # Log all API exceptions with context
    log_level = "error" if isinstance(exc, custom_exceptions) else "warning"
    log_message = (
        f"API Exception: {type(exc).__name__} - "
        f"User: {user_id}, "
        f"Path: {path}, "
        f"View: {view_name}, "
        f"Detail: {str(exc)}"
    )

    if log_level == "error":
        logger.error(log_message)
    else:
        logger.warning(log_message)

    # Call default exception handler
    response = exception_handler(exc, context)

    if response is not None:
        # Add additional information to response
        if hasattr(response, "data") and isinstance(response.data, dict):
            response.data["timestamp"] = timezone.now().isoformat()
            response.data["view"] = view_name

            # Mask details in production for security
            if not settings.DEBUG and "details" in response.data:
                response.data["details"] = "Internal server error"

    return response
