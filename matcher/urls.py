from django.urls import path

from .views import MatchPokemonView

app_name = "matcher"

urlpatterns = [
    path("match/", MatchPokemonView.as_view(), name="match-pokemon"),
]
