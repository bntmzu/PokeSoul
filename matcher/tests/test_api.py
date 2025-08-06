import pytest
from rest_framework.test import APIClient

from matcher.matching_engine import MatchingEngine
from matcher.tests.factories import PokemonFactory, UserProfileFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_pokemons(db):
    """Creates test Pokémon using factory_boy"""
    return [
        PokemonFactory(
            name="Charizard",
            types=["fire", "flying"],
            color="red",
            habitat="mountain",
            abilities=["blaze", "solar-power"],
            flavor_text="Spits fire hot enough to melt boulders.",
            hp=78,
            attack=84,
            defense=78,
            special_attack=109,
            special_defense=85,
            speed=100,
            popularity_score=50,
        ),
        PokemonFactory(
            name="Blastoise",
            types=["water"],
            color="blue",
            habitat="sea",
            abilities=["torrent", "rain-dish"],
            flavor_text="Crushes foes under its heavy body.",
            hp=79,
            attack=83,
            defense=100,
            special_attack=85,
            special_defense=105,
            speed=78,
            popularity_score=50,
        ),
    ]


# Create a simple matching engine for testing
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "answers, expected_name",
    [
        (
            {
                "time_of_day": "fire_red",
                "element_resonance": "fire",
                "conflict_handling": "attack",
                "favorite_color": "red",
                "place_you_belong": "mountain",
            },
            "Charizard",
        ),
        (
            {
                "time_of_day": "water_blue",
                "element_resonance": "water",
                "conflict_handling": "defense",
                "favorite_color": "blue",
                "place_you_belong": "sea",
            },
            "Blastoise",
        ),
    ],
)
def test_match_pokemon_profiles(api_client, test_pokemons, answers, expected_name):
    """Test matching returns correct Pokémon based on profile"""
    user_profile = UserProfileFactory(answers=answers)

    # Use SimpleMatchingEngine for testing
    engine = SimpleMatchingEngine(user_profile)
    result = engine.find_and_save_match()

    # Verify the result
    assert result is not None
    assert result.pokemon.name == expected_name
    assert result.total_score > 0

    # Debug: show match profile and scores
    print(f"\nExpected: {expected_name}")
    print(f"Match profile: {engine.match_profile}")
    print("All pokemons and their scores:")
    from pokemons.models import Pokemon

    for pokemon in Pokemon.objects.all():
        score = engine._calculate_match_score(pokemon)
        print(
            f"  {pokemon.name}: {score:.4f} (types: {pokemon.types}, color: {pokemon.color}, habitat: {pokemon.habitat})"
        )
    print(f"Matched: {result.pokemon.name}, score: {result.total_score}")
