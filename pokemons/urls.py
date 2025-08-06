from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pokemons.views import PokemonSearchView, PokemonViewSet

router = DefaultRouter()
router.register(r"", PokemonViewSet)  # /api/pokemons/

urlpatterns = [
    path("search/", PokemonSearchView.as_view(), name="pokemon-search"),
    path("", include(router.urls)),
]
