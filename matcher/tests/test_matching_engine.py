import pytest

from matcher.tests.factories import PokemonFactory, UserProfileFactory
from matcher.tests.test_utils import SimpleMatchingEngine


@pytest.mark.django_db
@pytest.mark.parametrize(
    "profile_answers,expected_pokemon_name",
    [
        # Test case 1: Fire-type preference with mountain habitat
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
        # Test case 2: Water-type preference with sea habitat
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
        # Test case 3: Grass-type preference with speed focus
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
    """Test matching engine with different personality profiles"""
    # Create test pokemons with specific characteristics
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

    # Create user profile with test answers
    user_profile = UserProfileFactory(answers=profile_answers)

    # Run matcher
    engine = SimpleMatchingEngine(user_profile)

    result = engine.find_and_save_match()

    assert result is not None
    assert result.pokemon.name == expected_pokemon_name
