import logging
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from django.db import transaction

from matcher.cache import cache_match_result, get_answers_hash, get_cached_match
from matcher.constants import ARCHETYPE_STATS, SCORES
from matcher.dataclasses import MatchScore
from matcher.models import MatchResult
from matcher.preference_extractor import PreferenceExtractor
from pokemons.models import Pokemon

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Simple matching engine using database Pokemon only"""

    def __init__(self, user_profile):
        self.user_profile = user_profile
        self.extractor = PreferenceExtractor(user_profile)
        self.match_profile = self.extractor.get_match_profile()

        # Create hash for caching
        self.answers_hash = get_answers_hash(self.user_profile.answers)
        logger.debug(f"Answers hash: {self.answers_hash[:8]}... (truncated)")

        # Check cache first
        cached_result = get_cached_match(self.answers_hash)
        if cached_result:
            logger.debug(f"Cache hit for hash {self.answers_hash[:8]}...")
            try:
                # Convert string UUID back to UUID object for database query
                pokemon_id = cached_result["pokemon_id"]
                score = cached_result["score"]

                pokemon = Pokemon.objects.get(id=pokemon_id)
                logger.debug(
                    f"Retrieved cached Pokemon: {pokemon.name} (score: {score})"
                )
                # Store cached result for later use
                self.cached_pokemon = pokemon
                self.cached_score = score
            except (Pokemon.DoesNotExist, KeyError, ValueError):
                logger.debug("Cached data invalid, performing fresh matching")
                pass  # Continue to fresh matching

        logger.debug(
            f"Cache miss, performing full matching for hash {self.answers_hash[:8]}... (truncated)"
        )

    def find_best_match(self) -> Optional[Tuple[Pokemon, float]]:
        """Finds the best Pokemon from database"""
        logger.debug(f"Finding best match for UserProfile {self.user_profile.id}")
        logger.debug(f"Match profile: {self.match_profile}")

        # Return cached result if available
        if hasattr(self, "cached_pokemon") and hasattr(self, "cached_score"):
            logger.debug(
                f"Using cached result: {self.cached_pokemon.name} (score: {self.cached_score})"
            )
            return self.cached_pokemon, self.cached_score

        # Get all Pokemon from database
        pokemons = Pokemon.objects.all()
        logger.debug(f"Found {pokemons.count()} Pokemon in database")

        return self._find_best_among_pokemons(pokemons)

    def _find_best_among_pokemons(
        self, pokemons: List[Pokemon]
    ) -> Optional[Tuple[Pokemon, float]]:
        """Find best match among Pokemon objects"""
        best_match = None
        best_score = 0.0
        top_scores: List[MatchScore] = []

        for pokemon in pokemons:
            score = self._calculate_match_score(pokemon)
            match_score = MatchScore(
                pokemon_name=pokemon.name,
                total_score=score,
                type_score=self._score_types(pokemon.types, self.match_profile.types),
                color_score=self._score_color(pokemon.color, self.match_profile.color),
                habitat_score=self._score_habitat(
                    pokemon.habitat, self.match_profile.habitat
                ),
                ability_score=self._score_abilities(
                    pokemon.abilities, self.match_profile.ability_keywords
                ),
                stats_score=self._score_base_stats(
                    pokemon, self.match_profile.personality_tags
                ),
                personality_score=self._score_personality(
                    pokemon, self.match_profile.personality_tags
                ),
            )
            top_scores.append(match_score)
            if score > best_score:
                best_score = score
                best_match = (pokemon, score)

        # Show top 5 scores
        top_scores.sort(key=lambda x: x.total_score, reverse=True)
        logger.debug(
            f"Top 5 Pokemon scores: {[(s.pokemon_name, s.total_score) for s in top_scores[:5]]}"
        )

        return best_match

    def create_match_result(self, pokemon: Pokemon, total_score: float) -> MatchResult:
        """Creates a match result"""
        match_result = MatchResult.objects.create(
            user_profile=self.user_profile,
            pokemon=pokemon,
            total_score=total_score,
        )
        return match_result

    def find_and_save_match(self) -> Optional[MatchResult]:
        """Finds the best Pokemon and saves the result with caching"""
        logger.debug(
            f"Starting matching process for UserProfile {self.user_profile.id}"
        )
        logger.debug(f"Match profile: {self.match_profile}")
        logger.debug(f"Answers hash: {self.answers_hash[:8]}... (truncated)")

        # Use cached result if available from __init__
        if hasattr(self, "cached_pokemon") and hasattr(self, "cached_score"):
            logger.debug(
                f"Using cached result: {self.cached_pokemon.name} (score: {self.cached_score})"
            )
            with transaction.atomic():
                match_result = MatchResult.objects.create(
                    user_profile=self.user_profile,
                    pokemon=self.cached_pokemon,
                    total_score=self.cached_score,
                )
            return match_result

        # Perform fresh matching only if no cache
        logger.debug(
            f"Cache miss, performing full matching for hash {self.answers_hash[:8]}..."
        )

        # Get all Pokemon from database
        pokemons = Pokemon.objects.all()
        logger.debug(f"Found {pokemons.count()} Pokemon in database")

        best_match = self._find_best_among_pokemons(pokemons)

        if best_match:
            pokemon, total_score = best_match
            logger.debug(f"Best match found: {pokemon.name} with score {total_score}")

            # Cache the result for future requests
            cache_match_result(self.answers_hash, pokemon.id, total_score)

            # Save to database
            with transaction.atomic():
                match_result = MatchResult.objects.create(
                    user_profile=self.user_profile,
                    pokemon=pokemon,
                    total_score=total_score,
                )

            return match_result

        logger.debug("No match found")
        return None

    def _calculate_match_score(self, pokemon: Pokemon) -> float:
        """Calculates overall match score"""
        type_score = self._score_types(pokemon.types, self.match_profile.types)
        color_score = self._score_color(pokemon.color, self.match_profile.color)
        habitat_score = self._score_habitat(pokemon.habitat, self.match_profile.habitat)
        ability_score = self._score_abilities(
            pokemon.abilities, self.match_profile.ability_keywords
        )
        stats_score = self._score_base_stats(
            pokemon, self.match_profile.personality_tags
        )
        personality_score = self._score_personality(
            pokemon, self.match_profile.personality_tags
        )

        total_score = (
            SCORES["types"] * type_score
            + SCORES["color"] * color_score
            + SCORES["habitat"] * habitat_score
            + SCORES["abilities"] * ability_score
            + SCORES["base_stats"] * stats_score
            + SCORES["flavor_text"] * personality_score
        )

        return total_score

    def _score_types(
        self, pokemon_types: List[str], preferred_types: List[str]
    ) -> float:
        """Score for Pokemon types with improved matching"""
        if not preferred_types:
            return 0.0

        pokemon_type_set = set(pokemon_types)
        preferred_type_set = set(preferred_types)
        intersection = pokemon_type_set & preferred_type_set

        # Perfect match bonus
        if len(intersection) == len(preferred_type_set):
            return 1.0

        # Partial match
        if intersection:
            return len(intersection) / len(preferred_type_set)

        return 0.0

    def _score_color(self, pokemon_color: str, preferred_color: str) -> float:
        """Score for color"""
        if not pokemon_color or not preferred_color:
            return 0.0
        return SequenceMatcher(
            None, pokemon_color.lower(), preferred_color.lower()
        ).ratio()

    def _score_habitat(self, pokemon_habitat: str, preferred_habitat: str) -> float:
        """Score for habitat"""
        if not pokemon_habitat or not preferred_habitat:
            return 0.0
        return SequenceMatcher(
            None, pokemon_habitat.lower(), preferred_habitat.lower()
        ).ratio()

    def _score_abilities(
        self, pokemon_abilities: List[str], preferred_abilities: List[str]
    ) -> float:
        """Score for abilities using string similarity"""
        if not pokemon_abilities or not preferred_abilities:
            return 0.0

        total_score = 0.0
        for ability in pokemon_abilities:
            for preferred_ability in preferred_abilities:
                similarity = SequenceMatcher(
                    None, ability.lower(), preferred_ability.lower()
                ).ratio()
                total_score += similarity

        return total_score / (len(pokemon_abilities) * len(preferred_abilities))

    def _score_base_stats(self, pokemon: Pokemon, personality_tags: List[str]) -> float:
        """Score for base stats based on archetypes"""
        relevant_stats = set()
        for tag in personality_tags:
            relevant_stats.update(ARCHETYPE_STATS.get(tag, []))

        if not relevant_stats:
            return 0.0

        pokemon_stats = {
            "hp": pokemon.hp,
            "attack": pokemon.attack,
            "defense": pokemon.defense,
            "special-attack": pokemon.special_attack,
            "special-defense": pokemon.special_defense,
            "speed": pokemon.speed,
        }

        total_score = sum(pokemon_stats.get(stat, 0) for stat in relevant_stats)
        max_possible = len(relevant_stats) * 150  # maximum stat value
        return total_score / max_possible if max_possible > 0 else 0.0

    def _score_personality(
        self, pokemon: Pokemon, personality_tags: List[str]
    ) -> float:
        """Score for personality using string similarity"""
        if not pokemon.flavor_text or not personality_tags:
            return 0.0

        personality_text = " ".join(personality_tags)
        return SequenceMatcher(
            None, pokemon.flavor_text.lower(), personality_text.lower()
        ).ratio()
