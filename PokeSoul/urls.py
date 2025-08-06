from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="PokeSoul API",
        default_version="v1",
        description="Explore and match Pokémon using personality traits.",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),  # Main app at root
    path("api/pokemons/", include("pokemons.urls")),
    path("api/matcher/", include("matcher.urls")),
    # Swagger UI
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]
