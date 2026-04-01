from dataclasses import dataclass, field
from typing import List, Optional

from packages.shared_schema import EvaluationResult, KnowledgeDocument, QuestionAtom, UserAttempt


@dataclass
class AssessmentRequest:
    attempt: UserAttempt
    question: Optional[QuestionAtom] = None
    context_documents: List[KnowledgeDocument] = field(default_factory=list)


@dataclass
class AssessmentResultBundle:
    evaluation: Optional[EvaluationResult] = None
    feedback_summary: str = ""
    followup_topics: List[str] = field(default_factory=list)
