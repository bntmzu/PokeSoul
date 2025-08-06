import requests
from requests.exceptions import HTTPError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)


# Custom exception for PokeAPI-related errors
class PokemonAPIError(Exception):
    pass


# Create a shared session for connection reuse and global headers
session = requests.Session()
session.headers.update(
    {
        "User-Agent": "PokemonEcho/1.0 (contact@example.com)",
        "Accept": "application/json",
    }
)


# Retry logic: exponential backoff + random jitter to avoid API overloading
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10) + wait_random(0, 1.5),
    retry=retry_if_exception_type((requests.exceptions.RequestException, HTTPError)),
)
def _get_json(url: str) -> dict:
    """
    Performs a GET request with retry, timeout, error handling, and JSON parsing.
    """
    try:
        response = session.get(
            url, timeout=(3.05, 10)
        )  # (connect_timeout, read_timeout)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, HTTPError) as e:
        raise PokemonAPIError(f"PokeAPI request failed for {url}: {e}") from e
    except ValueError:
        raise PokemonAPIError(f"Invalid JSON received from {url}")


def get_full_pokemon_data(name: str | int) -> dict:
    """
    Fetches and returns normalized Pokémon data from PokeAPI.
    """
    poke_url = f"https://pokeapi.co/api/v2/pokemon/{str(name).lower()}"
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{str(name).lower()}"

    poke_response = _get_json(poke_url)
    species_response = _get_json(species_url)

    # Normalize stats
    base_stats = {
        stat["stat"]["name"].replace("-", "_"): stat["base_stat"]
        for stat in poke_response.get("stats", [])
    }

    # Get first English flavor text
    flavor_text = next(
        (
            entry["flavor_text"].replace("\n", " ").replace("\f", " ")
            for entry in species_response.get("flavor_text_entries", [])
            if entry.get("language", {}).get("name") == "en"
        ),
        "No flavor text",
    )

    return {
        "name": poke_response["name"],
        "types": [t["type"]["name"] for t in poke_response.get("types", [])],
        "color": species_response.get("color", {}).get("name", "unknown"),
        "habitat": species_response.get("habitat", {}).get("name", "unknown"),
        "abilities": [a["ability"]["name"] for a in poke_response.get("abilities", [])],
        "flavor_text": flavor_text,
        "base_stats": {
            "hp": base_stats.get("hp", 0),
            "attack": base_stats.get("attack", 0),
            "defense": base_stats.get("defense", 0),
            "special_attack": base_stats.get("special_attack", 0),
            "special_defense": base_stats.get("special_defense", 0),
            "speed": base_stats.get("speed", 0),
        },
        # used for popularity calculation
        "held_items": poke_response.get("held_items", []),
        "moves": poke_response.get("moves", []),
        "game_indices": poke_response.get("game_indices", []),
        "image_url": poke_response.get("sprites", {}).get("front_default"),
        "cries_url": poke_response.get("cries", {}).get("latest"),
    }
