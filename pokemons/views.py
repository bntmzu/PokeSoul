from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from requests.exceptions import RequestException
from pokemons.serializers import PokemonDataSerializer, PokemonModelSerializer
from pokemons.pokeapi import get_full_pokemon_data, PokemonAPIError
from pokemons.models import Pokemon

class PokemonMatchView(APIView):
    def post(self, request):
        name = request.data.get("name") or "pikachu"  # docasne

        if not name:
            return Response({"error": "Missing 'name'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            raw_data = get_full_pokemon_data(name)
        except PokemonAPIError as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except (KeyError, TypeError, ValueError, RequestException):
            return Response({"error": "Malformed response from PokeAPI"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            serializer = PokemonDataSerializer(data=raw_data)
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({"error": "Invalid data from PokeAPI"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(serializer.data, status=status.HTTP_200_OK)

class PokemonViewSet(viewsets.ModelViewSet):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonModelSerializer

