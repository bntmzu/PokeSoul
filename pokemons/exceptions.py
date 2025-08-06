from rest_framework.exceptions import APIException


class PokemonNotFound(APIException):
    """Custom exception for when Pokemon is not found"""

    status_code = 404
    default_detail = "Pokemon not found."
    default_code = "pokemon_not_found"


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


class PokemonNameRequired(APIException):
    """Custom exception for missing Pokemon name"""

    status_code = 400
    default_detail = "Pokemon name is required."
    default_code = "pokemon_name_required"
