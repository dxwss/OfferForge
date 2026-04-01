from dataclasses import dataclass, field
from typing import List, Optional

from packages.shared_schema import EvaluationResult, UserAttempt, UserProfile, UserSkillState


@dataclass
class UserModelingRequest:
    profile: Optional[UserProfile] = None
    attempts: List[UserAttempt] = field(default_factory=list)
    evaluations: List[EvaluationResult] = field(default_factory=list)


@dataclass
class UserModelingResult:
    profile: Optional[UserProfile] = None
    skill_states: List[UserSkillState] = field(default_factory=list)
    memory_notes: List[str] = field(default_factory=list)
