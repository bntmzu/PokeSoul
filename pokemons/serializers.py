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
    """Serializer for validating Pokemon data from PokeAPI"""

    name = serializers.CharField(max_length=100)
    types = serializers.ListField(child=serializers.CharField(max_length=50))
    color = serializers.CharField(max_length=50, allow_blank=True, required=False)
    habitat = serializers.CharField(max_length=50, allow_blank=True, required=False)
    abilities = serializers.ListField(child=serializers.CharField(max_length=100))
    flavor_text = serializers.CharField(allow_blank=True, required=False)
    base_stats = serializers.DictField()
    image_url = serializers.URLField(allow_blank=True, required=False)
    cries_url = serializers.URLField(allow_blank=True, required=False)
    popularity_score = serializers.IntegerField(required=False, default=0)


class PokemonModelSerializer(serializers.ModelSerializer):
    base_stats = serializers.SerializerMethodField()

    class Meta:
        model = Pokemon
        fields = [
            "id",
            "name",
            "types",
            "color",
            "habitat",
            "abilities",
            "flavor_text",
            "hp",
            "attack",
            "defense",
            "special_attack",
            "special_defense",
            "speed",
            "base_stats",
            "image_url",
            "cries_url",
            "popularity_score",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_base_stats(self, obj):
        """Returns stats in base_stats format"""
        return {
            "hp": obj.hp,
            "attack": obj.attack,
            "defense": obj.defense,
            "special_attack": obj.special_attack,
            "special_defense": obj.special_defense,
            "speed": obj.speed,
        }

    def to_internal_value(self, data):
        """Supports both formats: with base_stats and flat fields"""
        # If data comes with base_stats, extract them
        if "base_stats" in data:
            base_stats = data.pop("base_stats")
            data.update(base_stats)

        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Formats data for API response"""
        data = super().to_representation(instance)
        # Remove flat stat fields from response
        for field in [
            "hp",
            "attack",
            "defense",
            "special_attack",
            "special_defense",
            "speed",
        ]:
            data.pop(field, None)
        return data
