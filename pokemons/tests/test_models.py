import pytest

from pokemons.models import Pokemon


@pytest.mark.django_db
def test_pokemon_model_creation():
    # Create a test instance
    pokemon = Pokemon.objects.create(
        name="Eevee",
        types=["normal"],
        color="brown",
        habitat="urban",
        abilities=["run-away", "adaptability"],
        flavor_text="It has the ability to alter the composition of its body to suit its surrounding environment.",
        hp=55,
        attack=55,
        defense=50,
        special_attack=45,
        special_defense=65,
        speed=55,
    )

    # Check values
    assert pokemon.name == "Eevee"
    assert pokemon.types == ["normal"]
    assert pokemon.color == "brown"
    assert pokemon.hp == 55
    assert pokemon.speed == 55
    assert "adaptability" in pokemon.abilities
    assert pokemon.created_at is not None
