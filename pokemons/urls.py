from django.urls import path, include
from pokemons.views import PokemonMatchView, PokemonViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", PokemonViewSet)  # /api/pokemons/

urlpatterns = [
    path("match/", PokemonMatchView.as_view(), name="pokemon-match"),
    path("", include(router.urls)),
]
