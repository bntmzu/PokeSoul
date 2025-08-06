import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class Pokemon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    types = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    color = models.CharField(max_length=50, null=True, blank=True)
    habitat = models.CharField(max_length=50, null=True, blank=True)
    abilities = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    flavor_text = models.TextField(null=True, blank=True)

    hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    special_attack = models.IntegerField()
    special_defense = models.IntegerField()
    speed = models.IntegerField()

    image_url = models.URLField(null=True, blank=True)
    cries_url = models.URLField(null=True, blank=True)
    popularity_score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Pokemon"
        verbose_name_plural = "Pokemons"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["types"]),
            models.Index(fields=["color"]),
            models.Index(fields=["habitat"]),
        ]

    def __str__(self):
        return self.name.capitalize()
