from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class UserPreferences:
    """Data structure for user preferences extracted from questionnaire answers"""

    types: List[str]
    colors: List[str]
    habitats: List[str]
    abilities: List[str]
    personality_tags: List[str]
    stat_preferences: Dict[str, int]


@dataclass
class MatchProfile:
    """Data structure for matching profile used by the matching engine"""

    types: List[str]
    color: Optional[str]
    habitat: Optional[str]
    ability_keywords: List[str]
    personality_tags: List[str]
    stat_preferences: Dict[str, int]


@dataclass
class MatchScore:
    """Data structure for detailed match scoring results"""

    pokemon_name: str
    total_score: float
    type_score: float
    color_score: float
    habitat_score: float
    ability_score: float
    stats_score: float
    personality_score: float


@dataclass
class MatchResultData:
    """Data structure for API response match result"""

    user_profile_id: str
    pokemon_id: str
    total_score: float
    pokemon_name: str
