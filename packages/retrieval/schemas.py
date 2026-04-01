from dataclasses import dataclass, field
from typing import List, Optional

from packages.shared_schema import KnowledgeDocument, QuestionAtom


@dataclass
class RetrievalRequest:
    user_id: Optional[str] = None
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    topic_tags: List[str] = field(default_factory=list)
    limit: int = 10


@dataclass
class RetrievalResult:
    candidate_questions: List[QuestionAtom] = field(default_factory=list)
    evidence_documents: List[KnowledgeDocument] = field(default_factory=list)
    debug_notes: List[str] = field(default_factory=list)
