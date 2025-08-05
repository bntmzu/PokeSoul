from rest_framework import serializers
from pokemons.models import Pokemon


class PokemonStatsSerializer(serializers.Serializer):
    hp = serializers.IntegerField()
    attack = serializers.IntegerField()
    defense = serializers.IntegerField()
    special_attack = serializers.IntegerField()
    special_defense = serializers.IntegerField()
    speed = serializers.IntegerField()


class PokemonDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    types = serializers.ListField(child=serializers.CharField())
    color = serializers.CharField()
    habitat = serializers.CharField()
    abilities = serializers.ListField(child=serializers.CharField())
    flavor_text = serializers.CharField()
    base_stats = PokemonStatsSerializer()


class PokemonModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pokemon
        fields = "__all__"
