import requests
from requests.exceptions import HTTPError
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception_type

# Custom exception for PokeAPI-related errors
class PokemonAPIError(Exception):
    pass

# Create a shared session for connection reuse and global headers
session = requests.Session()
session.headers.update({
    "User-Agent": "PokemonEcho/1.0 (contact@example.com)",
    "Accept": "application/json"
})

# Retry logic: exponential backoff + random jitter to avoid API overloading
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10) + wait_random(0, 1.5),
    retry=retry_if_exception_type((requests.exceptions.RequestException, HTTPError))
)
def _get_json(url: str) -> dict:
    """
    Performs a GET request with retry, timeout, error handling, and JSON parsing.
    """
    try:
        response = session.get(url, timeout=(3.05, 10))  # (connect_timeout, read_timeout)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, HTTPError) as e:
        raise PokemonAPIError(f"PokeAPI request failed for {url}: {e}") from e
    except ValueError:
        raise PokemonAPIError(f"Invalid JSON received from {url}")

def get_full_pokemon_data(name: str) -> dict:
    """
    Fetches and returns normalized Pokémon data from PokeAPI.
    """
    poke_url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}"

    poke_response = _get_json(poke_url)
    species_response = _get_json(species_url)

    return {
        "name": poke_response["name"],
        "types": [t["type"]["name"] for t in poke_response.get("types", [])],
        "color": species_response.get("color", {}).get("name", "unknown"),
        "habitat": species_response.get("habitat", {}).get("name", "unknown"),
        "abilities": [a["ability"]["name"] for a in poke_response.get("abilities", [])],
        "flavor_text": next(
            (entry["flavor_text"].replace("\n", " ").replace("\f", " ")
             for entry in species_response.get("flavor_text_entries", [])
             if entry.get("language", {}).get("name") == "en"),
            "No flavor text"
        ),
        "base_stats": {
            stat["stat"]["name"].replace("-", "_"): stat["base_stat"]
            for stat in poke_response.get("stats", [])
        }
    }

