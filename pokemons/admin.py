from django.contrib import admin

from .models import Pokemon


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "habitat",
        "hp",
        "attack",
        "speed",
        "popularity_score",
        "created_at",
    )
    search_fields = ("name", "color", "habitat")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("name", "color", "habitat", "popularity_score")}),
        (
            "Base Stats",
            {
                "fields": (
                    "hp",
                    "attack",
                    "defense",
                    "special_attack",
                    "special_defense",
                    "speed",
                )
            },
        ),
        ("Media", {"fields": ("image_url", "cries_url")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
