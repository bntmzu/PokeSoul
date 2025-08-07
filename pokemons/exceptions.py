from rest_framework.exceptions import APIException


class PokemonAPIUnavailable(APIException):
    """Custom exception for when PokeAPI is unavailable"""

    status_code = 502
    default_detail = "PokeAPI is currently unavailable."
    default_code = "pokeapi_unavailable"


class InvalidPokemonData(APIException):
    """Custom exception for invalid Pokemon data from PokeAPI"""

    status_code = 422
    default_detail = "Invalid Pokemon data received from PokeAPI."
    default_code = "invalid_pokemon_data"
