from django.db import models

from core.models import UserProfile
from pokemons.models import Pokemon


class MatchResult(models.Model):
    """Result of matching user with a Pokemon"""

    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="match_results"
    )
    pokemon = models.ForeignKey(
        Pokemon, on_delete=models.CASCADE, related_name="match_results"
    )

    # Overall match score
    total_score = models.FloatField(help_text="Overall match score")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-total_score", "-created_at"]
        verbose_name = "Match Result"
        verbose_name_plural = "Match Results"
        indexes = [
            models.Index(fields=["user_profile", "-total_score"]),
        ]

    def __str__(self):
        return f"{self.user_profile} → {self.pokemon} (Score: {self.total_score:.2f})"
