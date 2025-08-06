import logging

from django.conf import settings
from django.utils import timezone
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Global exception handler for API responses"""

    # Log errors for debugging
    logger.error(f"API Error: {exc} in {context['view'].__class__.__name__}")

    # Call default exception handler
    response = exception_handler(exc, context)

    if response is not None:
        # Add additional information to response
        response.data["timestamp"] = timezone.now().isoformat()
        response.data["view"] = context["view"].__class__.__name__

        # Mask details in production for security
        if not settings.DEBUG and "details" in response.data:
            response.data["details"] = "Internal server error"

    return response
