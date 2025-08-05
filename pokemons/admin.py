from django.contrib import admin
from .models import Pokemon


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "habitat", "hp", "attack", "speed", "created_at")
    search_fields = ("name", "color", "habitat")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("name", "color", "habitat")}),
        ("Base Stats", {"fields": ("hp", "attack", "defense", "special_attack", "special_defense", "speed")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
