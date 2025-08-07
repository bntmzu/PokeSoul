import pytest
from rest_framework.test import APIClient

from matcher.tests.factories import PokemonFactory, UserProfileFactory
from matcher.tests.test_utils import SimpleMatchingEngine


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

    # Verify the result
    assert result is not None
    assert result.pokemon.name == expected_name
    assert result.total_score > 0
