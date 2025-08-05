from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name.capitalize()
