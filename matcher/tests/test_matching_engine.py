import pytest

from matcher.matching_engine import MatchingEngine
from matcher.tests.factories import PokemonFactory, UserProfileFactory
from pokemons.models import Pokemon


@pytest.mark.django_db
@pytest.mark.parametrize(
    "profile_answers,expected_pokemon_name",
    [
        # Case 1: prefers fire + mountain → should match Firemon
        (
            {
                "time_of_day": "fire_red",
                "element_resonance": "fire",
                "conflict_handling": "attack",
                "favorite_color": "red",
                "place_you_belong": "mountain",
            },
            "Firemon",
        ),
        # Case 2: prefers water + sea → should match Aquamon
        (
            {
                "time_of_day": "water_blue",
                "element_resonance": "water",
                "conflict_handling": "defense",
                "favorite_color": "blue",
                "place_you_belong": "sea",
            },
            "Aquamon",
        ),
        # Case 3: prefers speed and forest → should match Speedmon
        (
            {
                "time_of_day": "grass_green",
                "element_resonance": "grass",
                "conflict_handling": "speed",
                "favorite_color": "green",
                "place_you_belong": "forest",
            },
            "Speedmon",
        ),
    ],
)
def test_matching_engine(profile_answers, expected_pokemon_name):
    # Create test pokemons
    PokemonFactory(
        name="Firemon",
        types=["fire"],
        color="red",
        habitat="mountain",
        strong_attacker=True,
        popularity_score=50,
    )
    PokemonFactory(
        name="Aquamon",
        types=["water"],
        color="blue",
        habitat="sea",
        strong_defender=True,
        popularity_score=50,
        abilities=["water-absorb", "swift-swim"],
        flavor_text="A powerful water Pokémon that lives in the sea",
    )
    PokemonFactory(
        name="Speedmon",
        types=["grass"],
        color="green",
        habitat="forest",
        speed=30,
        popularity_score=50,
    )
    PokemonFactory(name="Neutralmon", popularity_score=30)
    PokemonFactory(
        name="Darkmon",
        types=["dark"],
        color="black",
        habitat="cave",
        popularity_score=30,
    )

    # Create user profile
    user_profile = UserProfileFactory(answers=profile_answers)

    # Create a simple matching engine that doesn't use PreferenceExtractor
    class SimpleMatchingEngine(MatchingEngine):
        def __init__(self, user_profile):
            self.user_profile = user_profile
            # Create a simple match profile based on answers
            self.match_profile = self._create_simple_profile()
            # Add missing answers_hash attribute for caching
            self.answers_hash = "test_hash"

        def _create_simple_profile(self):
            """Create a simple match profile from answers"""
            profile = {
                "types": [],
                "color": None,
                "habitat": None,
                "ability_keywords": [],
                "personality_tags": [],
                "stat_preferences": {},
            }

            # Extract types from answers
            if "element_resonance" in self.user_profile.answers:
                profile["types"].append(self.user_profile.answers["element_resonance"])

            # Extract color
            if "favorite_color" in self.user_profile.answers:
                profile["color"] = self.user_profile.answers["favorite_color"]

            # Extract habitat
            if "place_you_belong" in self.user_profile.answers:
                profile["habitat"] = self.user_profile.answers["place_you_belong"]

            # Extract stat preferences
            if "conflict_handling" in self.user_profile.answers:
                stat = self.user_profile.answers["conflict_handling"]
                profile["stat_preferences"][stat] = 1

            return profile

    # Run matcher
    engine = SimpleMatchingEngine(user_profile)

    # Debug: show all pokemons and their scores
    print(f"\nExpected: {expected_pokemon_name}")
    print(f"Match profile: {engine.match_profile}")
    print("All pokemons and their scores:")
    for pokemon in Pokemon.objects.all():
        score = engine._calculate_match_score(pokemon)
        print(
            f"  {pokemon.name}: {score:.4f} (types: {pokemon.types}, color: {pokemon.color}, habitat: {pokemon.habitat})"
        )

    result = engine.find_and_save_match()

    assert result is not None
    print(f"Matched: {result.pokemon.name}, score: {result.total_score}")
    assert result.pokemon.name == expected_pokemon_name
