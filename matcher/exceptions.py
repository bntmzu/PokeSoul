from rest_framework.exceptions import APIException


class MatchingFailed(APIException):
    """Custom exception for when Pokemon matching fails"""

    status_code = 500
    default_detail = "Pokemon matching failed."
    default_code = "matching_failed"
