from dataclasses import dataclass, field
from typing import List, Optional

from packages.shared_schema import PracticePlan, QuestionAtom, QuestionRecommendation, UserProfile, UserSkillState


@dataclass
class PlanningRequest:
    profile: Optional[UserProfile] = None
    skill_states: List[UserSkillState] = field(default_factory=list)
    candidate_questions: List[QuestionAtom] = field(default_factory=list)
    target_company: Optional[str] = None
    target_role: Optional[str] = None


@dataclass
class PlanningResult:
    recommendation: Optional[QuestionRecommendation] = None
    practice_plan: Optional[PracticePlan] = None
    planner_notes: List[str] = field(default_factory=list)
