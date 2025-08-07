from pokemons.models import Pokemon

from .dataclasses import PokemonRawData, PokemonStats


def extract_base_stats(stats_dict: dict) -> PokemonStats:
    """Extract base stats from dictionary and return structured PokemonStats"""
    return PokemonStats(
        hp=stats_dict.get("hp", 0),
        attack=stats_dict.get("attack", 0),
        defense=stats_dict.get("defense", 0),
        special_attack=stats_dict.get("special_attack", 0),
        special_defense=stats_dict.get("special_defense", 0),
        speed=stats_dict.get("speed", 0),
    )


def estimate_popularity_score(poke_data: PokemonRawData) -> int:
    """Calculate popularity score based on Pokemon data from PokeAPI"""
    score = 0
    score += len(poke_data.game_indices)
    score += len(poke_data.held_items)
    score += len(poke_data.moves) // 10
    return score


def create_or_update_pokemon_from_raw(raw_data: dict) -> Pokemon:
    """Create or update Pokemon from raw PokeAPI data"""
    # Create structured data for better type safety
    base_stats = extract_base_stats(raw_data.get("base_stats", {}))

    pokemon_data = PokemonRawData(
        name=raw_data["name"],
        types=raw_data["types"],
        color=raw_data.get("color"),
        habitat=raw_data.get("habitat"),
        abilities=raw_data["abilities"],
        flavor_text=raw_data.get("flavor_text"),
        base_stats=base_stats,
        image_url=raw_data.get("image_url"),
        cries_url=raw_data.get("cries_url"),
        game_indices=raw_data.get("game_indices", []),
        held_items=raw_data.get("held_items", []),
        moves=raw_data.get("moves", []),
    )

    pokemon, _ = Pokemon.objects.update_or_create(
        name=pokemon_data.name,
        defaults={
            "types": pokemon_data.types,
            "color": pokemon_data.color,
            "habitat": pokemon_data.habitat,
            "abilities": pokemon_data.abilities,
            "flavor_text": pokemon_data.flavor_text,
            "hp": pokemon_data.base_stats.hp,
            "attack": pokemon_data.base_stats.attack,
            "defense": pokemon_data.base_stats.defense,
            "special_attack": pokemon_data.base_stats.special_attack,
            "special_defense": pokemon_data.base_stats.special_defense,
            "speed": pokemon_data.base_stats.speed,
            "image_url": pokemon_data.image_url,
            "cries_url": pokemon_data.cries_url,
            "popularity_score": estimate_popularity_score(pokemon_data),
        },
    )
    return pokemon
