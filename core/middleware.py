import logging
import time

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("core")


class PerformanceLoggingMiddleware(MiddlewareMixin):
    """Middleware to log request performance metrics"""

    def process_request(self, request):
        request.start_time = time.time()
        logger.debug(
            f"PerformanceLoggingMiddleware: Starting request {request.method} {request.path}"
        )
        return None

    def process_response(self, request, response):
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            logger.info(
                f"Request {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
        return response

    def process_exception(self, request, exception):
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            logger.error(
                f"Request {request.method} {request.path} - "
                f"Exception: {type(exception).__name__} - "
                f"Duration: {duration:.3f}s"
            )
        return None
