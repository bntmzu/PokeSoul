from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.exceptions import ValidationError
from requests.exceptions import RequestException
from pokemons.serializers import PokemonDataSerializer, PokemonModelSerializer
from pokemons.pokeapi import get_full_pokemon_data, PokemonAPIError
from pokemons.models import Pokemon
from pokemons.cache import get_pokemon_from_cache, set_pokemon_to_cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PokemonMatchView(APIView):

    @swagger_auto_schema(
        operation_summary="Match a Pokémon by name",
        operation_description="Fetches full Pokémon data (types, color, abilities, base stats) from PokeAPI, stores to DB if needed, and caches response.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Pokémon name to fetch"
                )
            },
        ),
        responses={
            200: openapi.Response(
                "Pokémon matched successfully", PokemonDataSerializer
            ),
            400: "Missing 'name'",
            422: "Invalid or malformed PokeAPI data",
            502: "PokeAPI is unavailable or returned an error",
        },
    )
    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response(
                {"error": "Missing 'name'"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Step 1: Try Redis
        cached_data = get_pokemon_from_cache(name)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Step 2: Try database
        try:
            pokemon = Pokemon.objects.get(name__iexact=name)
            model_data = PokemonModelSerializer(pokemon).data
            set_pokemon_to_cache(name, model_data)  # cache it
            return Response(model_data, status=status.HTTP_200_OK)
        except Pokemon.DoesNotExist:
            pass

        # Step 3: Fallback to PokeAPI
        try:
            raw_data = get_full_pokemon_data(name)
        except PokemonAPIError as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except (KeyError, TypeError, ValueError, RequestException):
            return Response(
                {"error": "Malformed response from PokeAPI"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Step 4: Validate external API response
        try:
            data_serializer = PokemonDataSerializer(data=raw_data)
            data_serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(
                {"error": "Invalid data from PokeAPI"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Step 5: Save to DB if not already there
        model_data = {**raw_data, **raw_data["base_stats"]}
        if not Pokemon.objects.filter(name__iexact=raw_data["name"]).exists():
            model_serializer = PokemonModelSerializer(data=model_data)
            if model_serializer.is_valid():
                model_serializer.save()
            else:
                return Response(
                    {
                        "error": "Failed to save to DB",
                        "details": model_serializer.errors,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        #  Step 6: Cache and return
        set_pokemon_to_cache(name, data_serializer.data)
        return Response(data_serializer.data, status=status.HTTP_200_OK)


class PokemonViewSet(viewsets.ModelViewSet):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonModelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "color", "habitat"]
    ordering_fields = ["hp", "attack", "defense", "speed", "created_at"]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        operation_summary="List all Pokémon",
        responses={
            200: openapi.Response("List of Pokémon", PokemonModelSerializer(many=True))
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve Pokémon by ID",
        responses={200: openapi.Response("Pokémon details", PokemonModelSerializer())},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new Pokémon",
        request_body=PokemonModelSerializer,
        responses={
            201: openapi.Response(
                "Pokémon created successfully", PokemonModelSerializer
            ),
            400: "Invalid input data",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
