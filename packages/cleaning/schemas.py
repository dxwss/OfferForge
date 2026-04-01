from dataclasses import dataclass, field
from typing import Dict, List

from packages.shared_schema import CleanedPost, RawPost


@dataclass
class CleaningRequest:
    raw_posts: List[RawPost]
    deduplicate: bool = True
    drop_irrelevant: bool = True
    min_relevance_score: float = 0.2


@dataclass
class CleaningStats:
    total_posts: int = 0
    cleaned_posts: int = 0
    dropped_posts: int = 0
    duplicate_posts: int = 0
    relevant_posts: int = 0


@dataclass
class CleaningResult:
    cleaned_posts: List[CleanedPost] = field(default_factory=list)
    dropped_post_ids: List[str] = field(default_factory=list)
    dedup_primary_by_post_id: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    stats: CleaningStats = field(default_factory=CleaningStats)
