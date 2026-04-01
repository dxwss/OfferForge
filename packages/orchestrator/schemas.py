from dataclasses import dataclass, field
from typing import List, Optional

from packages.shared_schema import PracticeSession, UserAttempt


@dataclass
class OrchestrationRequest:
    user_id: str
    session: Optional[PracticeSession] = None
    latest_attempt: Optional[UserAttempt] = None


@dataclass
class OrchestrationResult:
    next_action: str = "noop"
    session: Optional[PracticeSession] = None
    notes: List[str] = field(default_factory=list)
