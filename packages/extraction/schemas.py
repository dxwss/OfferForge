from dataclasses import dataclass, field
from typing import List, Optional

from packages.shared_schema import CleanedPost, InterviewEvent


@dataclass
class ExtractionRequest:
    cleaned_posts: List[CleanedPost]
    batch_id: Optional[str] = None
    include_debug_fields: bool = False


@dataclass
class ExtractionResult:
    events: List[InterviewEvent] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
