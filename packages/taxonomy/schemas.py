from dataclasses import dataclass, field
from typing import List

from packages.shared_schema import InterviewEvent


@dataclass
class TaxonomyResolutionRequest:
    events: List[InterviewEvent]
    allow_manual_overrides: bool = True


@dataclass
class TaxonomyResolutionResult:
    resolved_events: List[InterviewEvent] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
