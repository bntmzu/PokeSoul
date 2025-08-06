import factory
from factory.django import DjangoModelFactory

from core.models import UserProfile
from pokemons.models import Pokemon


class PokemonFactory(DjangoModelFactory):
    class Meta:
        model = Pokemon

    name = factory.Sequence(lambda n: f"Testmon{n}")
    types = ["normal"]
    color = "gray"
    habitat = "forest"
    abilities = ["run-away"]
    flavor_text = "Just a test Pokémon"
    hp = 50
    attack = 50
    defense = 50
    special_attack = 50
    special_defense = 50
    speed = 50
    popularity_score = factory.Faker("random_int", min=10, max=100)

    class Params:
        strong_attacker = factory.Trait(attack=90)
        strong_defender = factory.Trait(defense=100)
        fast = factory.Trait(speed=120)


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    answers: dict = {}
