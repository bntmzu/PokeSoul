from rest_framework.exceptions import APIException


class UserProfileNotFound(APIException):
    """Custom exception for when user profile is not found"""

    status_code = 404
    default_detail = "User profile not found."
    default_code = "user_profile_not_found"


class NoAnswersProvided(APIException):
    """Custom exception for when user profile has no answers"""

    status_code = 400
    default_detail = "User profile has no answers."
    default_code = "no_answers_provided"


class NoSuitablePokemon(APIException):
    """Custom exception for when no suitable Pokemon is found"""

    status_code = 404
    default_detail = "No suitable Pokemon found for this profile."
    default_code = "no_suitable_pokemon"


class MatchingFailed(APIException):
    """Custom exception for when Pokemon matching fails"""

    status_code = 500
    default_detail = "Pokemon matching failed."
    default_code = "matching_failed"
