from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class MatchResponse:
    """Data structure for match API response"""

    user_profile_id: UUID
    pokemon: Dict[str, Any]
    match_score: float
    message: str


@dataclass
class ErrorResponse:
    """Data structure for API error responses"""

    error: str
    code: str
    details: Optional[str] = None


@dataclass
class UserProfileData:
    """Data structure for user profile information"""

    id: UUID
    answers: Dict[str, str]
    created_at: str


@dataclass
class QuestionData:
    """Data structure for questionnaire questions"""

    identifier: str
    text: str
    options: List[Dict[str, Any]]
