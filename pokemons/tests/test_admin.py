import pytest
from django.contrib.admin.sites import AdminSite

from pokemons.admin import PokemonAdmin
from pokemons.models import Pokemon


@pytest.fixture
def admin_instance():
    return PokemonAdmin(Pokemon, AdminSite())


def test_admin_list_display_fields(admin_instance):
    assert admin_instance.list_display == (
        "name",
        "color",
        "habitat",
        "hp",
        "attack",
        "speed",
        "popularity_score",
        "created_at",
    )


def test_admin_search_fields(admin_instance):
    assert admin_instance.search_fields == ("name", "color", "habitat")


def test_admin_ordering(admin_instance):
    assert admin_instance.ordering == ("-created_at",)


def test_admin_readonly_fields(admin_instance):
    assert "created_at" in admin_instance.readonly_fields


def test_admin_fieldsets_structure(admin_instance):
    fieldsets = dict(admin_instance.fieldsets)

    assert "name" in fieldsets[None]["fields"]
    assert "hp" in fieldsets["Base Stats"]["fields"]
    assert "created_at" in fieldsets["Timestamps"]["fields"]
