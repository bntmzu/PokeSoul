import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from pokemons.models import Pokemon
from pokemons.serializers import PokemonModelSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_serializer_directly():
    """Direct serializer test"""
    data = {
        "name": "test",
        "types": ["normal"],
        "color": "white",
        "habitat": "forest",
        "abilities": ["test"],
        "flavor_text": "Test pokemon",
        "hp": 50,
        "attack": 50,
        "defense": 50,
        "special_attack": 50,
        "special_defense": 50,
        "speed": 50,
    }
    serializer = PokemonModelSerializer(data=data)
    assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
    pokemon = serializer.save()
    assert pokemon.name == "test"
    assert pokemon.hp == 50


@pytest.mark.django_db
def test_match_existing_pokemon_in_db(api_client):
    Pokemon.objects.create(
        name="bulbasaur",
        types=["grass", "poison"],
        color="green",
        habitat="forest",
        abilities=["overgrow"],
        flavor_text="Test text.",
        hp=45,
        attack=49,
        defense=49,
        special_attack=65,
        special_defense=65,
        speed=45,
    )
    url = reverse("pokemon-search")
    response = api_client.post(url, {"name": "bulbasaur"}, format="json")
    assert response.status_code == 200
    assert response.data["name"] == "bulbasaur"
    # Check the new base_stats structure
    assert "base_stats" in response.data
    assert response.data["base_stats"]["hp"] == 45
    assert response.data["base_stats"]["attack"] == 49


@pytest.mark.django_db
def test_match_invalid_pokemon(api_client):
    url = reverse("pokemon-search")
    response = api_client.post(url, {"name": "invalidmon"}, format="json")
    assert response.status_code in [502, 422]
    assert "error" in response.data


@pytest.mark.django_db
def test_match_missing_name(api_client):
    url = reverse("pokemon-search")
    response = api_client.post(url, {}, format="json")
    assert response.status_code == 400
    assert "error" in response.data


@pytest.mark.django_db
def test_list_pokemons(api_client):
    Pokemon.objects.create(
        name="pikachu",
        types=["electric"],
        color="yellow",
        habitat="forest",
        abilities=["static"],
        flavor_text="Electric mouse.",
        hp=35,
        attack=55,
        defense=40,
        special_attack=50,
        special_defense=50,
        speed=90,
    )
    url = reverse("pokemon-list")
    response = api_client.get(url)
    assert response.status_code == 200
    pokemon_data = next(p for p in response.data if p["name"] == "pikachu")
    assert pokemon_data["name"] == "pikachu"
    # Check the new base_stats structure
    assert "base_stats" in pokemon_data
    assert pokemon_data["base_stats"]["hp"] == 35
    assert pokemon_data["base_stats"]["speed"] == 90


@pytest.mark.django_db
def test_create_pokemon(api_client):
    url = reverse("pokemon-list")
    # Now we need to send data in the new format with base_stats
    data = {
        "name": "charmander",
        "types": ["fire"],
        "color": "red",
        "habitat": "mountain",
        "abilities": ["blaze"],
        "flavor_text": "Fire lizard.",
        "base_stats": {
            "hp": 39,
            "attack": 52,
            "defense": 43,
            "special_attack": 60,
            "special_defense": 50,
            "speed": 65,
        },
    }
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == 201
    assert Pokemon.objects.filter(name="charmander").exists()
    # Check that data was saved correctly
    pokemon = Pokemon.objects.get(name="charmander")
    assert pokemon.hp == 39
    assert pokemon.attack == 52


@pytest.mark.django_db
def test_retrieve_pokemon(api_client):
    pokemon = Pokemon.objects.create(
        name="squirtle",
        types=["water"],
        color="blue",
        habitat="lake",
        abilities=["torrent"],
        flavor_text="Water turtle.",
        hp=44,
        attack=48,
        defense=65,
        special_attack=50,
        special_defense=64,
        speed=43,
    )
    url = reverse("pokemon-detail", kwargs={"pk": pokemon.id})
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["name"] == "squirtle"
    # Check the new base_stats structure
    assert "base_stats" in response.data
    assert response.data["base_stats"]["hp"] == 44
    assert response.data["base_stats"]["defense"] == 65


@pytest.mark.django_db
def test_create_pokemon_with_flat_stats(api_client):
    """Test for backward compatibility - creation with flat fields"""
    url = reverse("pokemon-list")
    data = {
        "name": "mewtwo",
        "types": ["psychic"],
        "color": "purple",
        "habitat": "cave",
        "abilities": ["pressure"],
        "flavor_text": "Genetic Pokémon.",
        "hp": 106,
        "attack": 110,
        "defense": 90,
        "special_attack": 154,
        "special_defense": 90,
        "speed": 130,
    }
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == 201
    assert Pokemon.objects.filter(name="mewtwo").exists()
    # Check that data was saved correctly
    pokemon = Pokemon.objects.get(name="mewtwo")
    assert pokemon.hp == 106
    assert pokemon.special_attack == 154
