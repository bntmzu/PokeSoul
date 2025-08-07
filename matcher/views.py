import logging

from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import UserProfile
from pokemons.serializers import PokemonModelSerializer

from .exceptions import (
    MatchingFailed,
)
from .matching_engine import MatchingEngine

logger = logging.getLogger(__name__)


class MatchPokemonView(APIView):
    """API for matching Pokemon based on user profile"""

    @swagger_auto_schema(
        operation_summary="Match Pokemon for user based on their profile",
        operation_description="Matches a Pokemon to a user based on their quiz answers and personality traits.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_profile_id"],
            properties={
                "user_profile_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_UUID,
                    description="UUID of the user profile to match",
                )
            },
        ),
        responses={
            200: openapi.Response(
                "Pokemon matched successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user_profile_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "pokemon": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="Matched Pokemon data"
                        ),
                        "match_score": openapi.Schema(
                            type=openapi.TYPE_NUMBER,
                            description="Overall match score (0-1)",
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Human-readable match message",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                "Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                        "code": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            404: openapi.Response(
                "User Profile Not Found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                        "code": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            422: openapi.Response("No answers provided for matching"),
            500: openapi.Response("Matching failed"),
        },
    )
    def post(self, request):
        """Match Pokemon for user based on their profile"""
        user_profile_id = request.data.get("user_profile_id")

        if not user_profile_id:
            return Response(
                {
                    "error": "user_profile_id is required",
                    "code": "missing_user_profile_id",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get user profile from database
            user_profile = get_object_or_404(UserProfile, id=user_profile_id)

            # Check if user has answers
            if not user_profile.answers:
                raise ValidationError("User profile has no answers")

            # Create matching engine and find best Pokemon
            engine = MatchingEngine(user_profile)
            match_result = engine.find_and_save_match()

            if not match_result:
                raise NotFound("No suitable Pokemon found for this profile")

            # Form response with full Pokemon information
            pokemon_data = PokemonModelSerializer(match_result.pokemon).data

            return Response(
                {
                    "user_profile_id": user_profile_id,
                    "pokemon": pokemon_data,
                    "match_score": match_result.total_score,
                    "message": f"Your Pokemon: {match_result.pokemon.name}! {match_result.pokemon.flavor_text}",
                },
                status=status.HTTP_200_OK,
            )

        except Http404:
            raise NotFound("User profile not found")
        except Exception as e:
            # Log unexpected errors for debugging
            logger.error(f"Matching failed: {str(e)}")
            raise MatchingFailed(detail=f"Matching failed: {str(e)}")
