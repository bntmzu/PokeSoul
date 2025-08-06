from pokemons.models import Pokemon


def extract_base_stats(stats_dict: dict) -> dict:
    return {
        "hp": stats_dict.get("hp", 0),
        "attack": stats_dict.get("attack", 0),
        "defense": stats_dict.get("defense", 0),
        "special_attack": stats_dict.get("special_attack", 0),
        "special_defense": stats_dict.get("special_defense", 0),
        "speed": stats_dict.get("speed", 0),
    }


def estimate_popularity_score(poke: dict) -> int:
    score = 0
    score += len(poke.get("game_indices", []))
    score += len(poke.get("held_items", []))
    score += len(poke.get("moves", [])) // 10
    return score


def create_or_update_pokemon_from_raw(raw_data: dict) -> Pokemon:
    base_stats = extract_base_stats(raw_data.get("base_stats", {}))

    pokemon, _ = Pokemon.objects.update_or_create(
        name=raw_data["name"],
        defaults={
            "types": raw_data["types"],
            "color": raw_data["color"],
            "habitat": raw_data["habitat"],
            "abilities": raw_data["abilities"],
            "flavor_text": raw_data["flavor_text"],
            **base_stats,
            "image_url": raw_data.get("image_url"),
            "cries_url": raw_data.get("cries_url"),
            "popularity_score": estimate_popularity_score(raw_data),
        },
    )
    return pokemon
