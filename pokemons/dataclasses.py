from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PokemonStats:
    """Data structure for Pokemon base stats"""

    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int


@dataclass
class PokemonRawData:
    """Data structure for raw PokeAPI response data"""

    name: str
    types: List[str]
    color: Optional[str]
    habitat: Optional[str]
    abilities: List[str]
    flavor_text: Optional[str]
    base_stats: PokemonStats
    image_url: Optional[str]
    cries_url: Optional[str]
    game_indices: List[Dict]
    held_items: List[Dict]
    moves: List[Dict]


@dataclass
class PokemonSearchResult:
    """Data structure for Pokemon search results"""

    name: str
    types: List[str]
    color: Optional[str]
    habitat: Optional[str]
    abilities: List[str]
    flavor_text: Optional[str]
    base_stats: PokemonStats
    image_url: Optional[str]
    cries_url: Optional[str]
    popularity_score: int
