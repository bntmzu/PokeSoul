# Scoring weights for different Pokemon attributes
SCORES = {
    "types": 0.5,  # Most important - Pokemon type matching
    "color": 0.2,
    "habitat": 0.15,
    "abilities": 0.1,
    "base_stats": 0.03,
    "flavor_text": 0.02,
}

# Archetype stats mapping for personality-based matching
ARCHETYPE_STATS = {
    "adventurous": ["speed", "attack"],
    "empathetic": ["special-defense", "hp"],
    "introspective": ["special-attack", "special-defense"],
    "intense": ["attack", "speed"],
    "calm": ["defense", "special-defense"],
    "chaotic": ["speed", "special-attack"],
    "strategic": ["special-attack", "defense"],
    "protective": ["defense", "hp"],
    "reckless": ["attack", "speed"],
    "wise": ["special-attack", "special-defense"],
}
