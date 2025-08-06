from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from requests.exceptions import RequestException
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from pokemons.cache import get_pokemon_from_cache, set_pokemon_to_cache
from pokemons.models import Pokemon
from pokemons.pokeapi import PokemonAPIError, get_full_pokemon_data
from pokemons.serializers import PokemonDataSerializer, PokemonModelSerializer


class PokemonSearchView(APIView):

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
                "Pokémon matched successfully", PokemonModelSerializer
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

        try:
            # 1. Redis cache
            cached = get_pokemon_from_cache(name)
            if cached:
                return Response(cached)

            # 2. Database
            db_result = self.get_pokemon_from_db(name)
            if db_result:
                return Response(db_result)

            # 3. External PokeAPI
            raw_data = self.fetch_from_pokeapi(name)

            # 4. Validate external data
            data_serializer = PokemonDataSerializer(data=raw_data)
            data_serializer.is_valid(raise_exception=True)

            # 5. Save to DB and return
            pokemon = self.save_pokemon_if_new(raw_data)
            model_serializer = PokemonModelSerializer(pokemon)

            # 6. Cache and return
            set_pokemon_to_cache(name, model_serializer.data)
            return Response(model_serializer.data, status=status.HTTP_200_OK)

        except ValidationError:
            return Response(
                {"error": "Invalid data from PokeAPI"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except PokemonAPIError as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response(
                {"error": "Unexpected server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_pokemon_from_db(self, name):
        try:
            pokemon = Pokemon.objects.get(name__iexact=name)
            serializer = PokemonModelSerializer(pokemon)
            set_pokemon_to_cache(name, serializer.data)
            return serializer.data
        except Pokemon.DoesNotExist:
            return None

    def fetch_from_pokeapi(self, name):
        try:
            return get_full_pokemon_data(name)
        except (KeyError, TypeError, ValueError, RequestException):
            raise ValidationError("Malformed response from PokeAPI")

    def save_pokemon_if_new(self, raw_data):
        pokemon, created = Pokemon.objects.get_or_create(
            name__iexact=raw_data["name"],
            defaults={
                "name": raw_data["name"],
                "types": raw_data["types"],
                "color": raw_data["color"],
                "habitat": raw_data["habitat"],
                "abilities": raw_data["abilities"],
                "flavor_text": raw_data["flavor_text"],
                "hp": raw_data["base_stats"]["hp"],
                "attack": raw_data["base_stats"]["attack"],
                "defense": raw_data["base_stats"]["defense"],
                "special_attack": raw_data["base_stats"]["special_attack"],
                "special_defense": raw_data["base_stats"]["special_defense"],
                "speed": raw_data["base_stats"]["speed"],
            },
        )
        return pokemon


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
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {"error": "Invalid input data", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": "Unexpected server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
