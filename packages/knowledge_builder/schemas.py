from dataclasses import dataclass, field
from typing import List

from packages.shared_schema import InterviewEvent, KnowledgeDocument, QuestionAtom


@dataclass
class KnowledgeBuildRequest:
    events: List[InterviewEvent]
    rebuild_existing: bool = False


@dataclass
class KnowledgeBuildResult:
    question_atoms: List[QuestionAtom] = field(default_factory=list)
    knowledge_documents: List[KnowledgeDocument] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
