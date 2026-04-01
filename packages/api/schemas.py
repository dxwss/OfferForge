from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class StartSessionRequest:
    user_id: str
    mode: str = "practice"
    target_company: Optional[str] = None
    target_role: Optional[str] = None


@dataclass
class SubmitAnswerRequest:
    user_id: str
    session_id: str
    question_id: str
    answer: str


@dataclass
class ApiResponse:
    success: bool = True
    message: str = "TODO"
    data: Dict[str, Any] = field(default_factory=dict)
