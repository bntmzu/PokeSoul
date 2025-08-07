import json
import logging
from typing import Any, Dict

from core.models import AnswerOption, Question, UserProfile

from .dataclasses import MatchProfile, UserPreferences

logger = logging.getLogger(__name__)


class PreferenceExtractor:
    """Extracts user preferences from questionnaire answers"""

    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile

    def extract_preferences(self) -> UserPreferences:
        """Extracts preferences from user answers"""
        preferences = UserPreferences(
            types=[],
            colors=[],
            habitats=[],
            abilities=[],
            personality_tags=[],
            stat_preferences={},
        )

        # Process each answer
        for question_id, answer_option_id in self.user_profile.answers.items():
            try:
                option = AnswerOption.objects.get(id=answer_option_id)

                # Parse JSON answer value from the option
                answer_data = json.loads(option.value)
                self._process_answer_data(answer_data, preferences)

            except (
                Question.DoesNotExist,
                AnswerOption.DoesNotExist,
                json.JSONDecodeError,
            ) as e:
                logger.debug(f"Error processing answer {question_id}: {e}")
                continue

        return preferences

    def _process_answer_data(
        self, answer_data: Dict[str, Any], preferences: UserPreferences
    ):
        """Process data from a single answer"""
        # Pokemon types
        if "type" in answer_data:
            pokemon_type = answer_data["type"]
            if pokemon_type not in preferences.types:
                preferences.types.append(pokemon_type)

        # Colors
        if "color" in answer_data:
            color = answer_data["color"]
            if color not in preferences.colors:
                preferences.colors.append(color)

        # Habitat
        if "habitat" in answer_data:
            habitat = answer_data["habitat"]
            if habitat not in preferences.habitats:
                preferences.habitats.append(habitat)

        # Abilities
        if "ability" in answer_data:
            ability = answer_data["ability"]
            if ability not in preferences.abilities:
                preferences.abilities.append(ability)

        # Stats
        if "stat" in answer_data:
            stat = answer_data["stat"]
            current_value = preferences.stat_preferences.get(stat, 0)
            preferences.stat_preferences[stat] = current_value + 1

        # Shapes/features
        if "shape" in answer_data:
            shape = answer_data["shape"]
            if shape not in preferences.personality_tags:
                preferences.personality_tags.append(shape)

    def get_personality_archetype(self, preferences: UserPreferences) -> str:
        """Determines personality archetype based on preferences"""
        archetype_scores = {
            "adventurous": 0,
            "empathetic": 0,
            "introspective": 0,
            "intense": 0,
            "calm": 0,
            "chaotic": 0,
            "strategic": 0,
            "protective": 0,
            "reckless": 0,
            "wise": 0,
        }

        # Analyze type preferences
        for pokemon_type in preferences.types:
            if pokemon_type in ["fire", "fighting", "dragon"]:
                archetype_scores["intense"] += 1
                archetype_scores["reckless"] += 1
            elif pokemon_type in ["water", "grass", "fairy"]:
                archetype_scores["empathetic"] += 1
                archetype_scores["calm"] += 1
            elif pokemon_type in ["psychic", "ghost"]:
                archetype_scores["introspective"] += 1
                archetype_scores["wise"] += 1
            elif pokemon_type in ["electric", "dark"]:
                archetype_scores["chaotic"] += 1
                archetype_scores["adventurous"] += 1
            elif pokemon_type in ["steel", "rock"]:
                archetype_scores["protective"] += 1
                archetype_scores["strategic"] += 1

        # Analyze stats
        for stat, value in preferences.stat_preferences.items():
            if stat == "attack":
                archetype_scores["intense"] += value
                archetype_scores["reckless"] += value
            elif stat == "defense":
                archetype_scores["protective"] += value
                archetype_scores["calm"] += value
            elif stat == "special-attack":
                archetype_scores["wise"] += value
                archetype_scores["introspective"] += value
            elif stat == "special-defense":
                archetype_scores["empathetic"] += value
                archetype_scores["strategic"] += value
            elif stat == "speed":
                archetype_scores["adventurous"] += value
                archetype_scores["chaotic"] += value

        # Return archetype with highest score
        return max(archetype_scores.items(), key=lambda x: x[1])[0]

    def get_match_profile(self) -> MatchProfile:
        """Returns profile for matching"""
        preferences = self.extract_preferences()
        archetype = self.get_personality_archetype(preferences)

        return MatchProfile(
            types=preferences.types,
            color=preferences.colors[0] if preferences.colors else None,
            habitat=preferences.habitats[0] if preferences.habitats else None,
            ability_keywords=preferences.abilities,
            personality_tags=preferences.personality_tags + [archetype],
            stat_preferences=preferences.stat_preferences,
        )
