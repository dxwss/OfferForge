from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from .config.defaults import DEFAULT_LANGUAGE, DEFAULT_RELIABILITY_SCORE, SCORE_MAX, SCORE_MIN


class SourceType(str, Enum):
    MANUAL_IMPORT = "manual_import"
    REDDIT = "reddit"
    ZHIHU = "zhihu"
    XIAOHONGSHU = "xiaohongshu"
    CSV_IMPORT = "csv_import"
    JSON_IMPORT = "json_import"
    API = "api"
    OTHER = "other"


class InterviewStageType(str, Enum):
    ONLINE_ASSESSMENT = "online_assessment"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    MANAGER = "manager"
    HR = "hr"
    BEHAVIORAL = "behavioral"
    OTHER = "other"


class QuestionType(str, Enum):
    CODING = "coding"
    KNOWLEDGE = "knowledge"
    SYSTEM_DESIGN = "system_design"
    PROJECT = "project"
    BEHAVIORAL = "behavioral"
    DEBUGGING = "debugging"
    OTHER = "other"


class SessionMode(str, Enum):
    PRACTICE = "practice"
    MOCK_INTERVIEW = "mock_interview"
    REVIEW = "review"
    PLANNING = "planning"


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


def _require_non_empty_text(field_name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a non-empty string." % field_name)


def _validate_non_negative_int(field_name: str, value: int) -> None:
    if not isinstance(value, int) or value < 0:
        raise ValueError("%s must be a non-negative integer." % field_name)


def _validate_positive_int(field_name: str, value: int) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError("%s must be a positive integer." % field_name)


def _validate_score(field_name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or value < SCORE_MIN or value > SCORE_MAX:
        raise ValueError("%s must be between %.1f and %.1f." % (field_name, SCORE_MIN, SCORE_MAX))


def _validate_string_list(field_name: str, values: List[str]) -> None:
    if not isinstance(values, list):
        raise ValueError("%s must be a list of strings." % field_name)
    for item in values:
        _require_non_empty_text(field_name, item)


def _parse_datetime(value: Optional[Any]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise TypeError("Expected datetime or ISO8601 string.")


def _parse_enum(enum_type: Type[Enum], value: Optional[Any]) -> Optional[Enum]:
    if value is None:
        return None
    if isinstance(value, enum_type):
        return value
    return enum_type(value)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {field_info.name: _serialize_value(getattr(value, field_info.name)) for field_info in fields(value)}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


@dataclass
class SchemaModel:
    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(self)


@dataclass
class TextSegment(SchemaModel):
    text: str
    start_char: int
    end_char: int
    segment_type: str = "paragraph"

    def __post_init__(self) -> None:
        _require_non_empty_text("text", self.text)
        _validate_non_negative_int("start_char", self.start_char)
        _validate_non_negative_int("end_char", self.end_char)
        if self.end_char <= self.start_char:
            raise ValueError("end_char must be greater than start_char.")
        _require_non_empty_text("segment_type", self.segment_type)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TextSegment":
        return cls(
            text=payload["text"],
            start_char=payload["start_char"],
            end_char=payload["end_char"],
            segment_type=payload.get("segment_type", "paragraph"),
        )


@dataclass
class EvidenceSpan(SchemaModel):
    span_id: str
    post_id: str
    field_name: str
    text: str
    start_char: int
    end_char: int
    confidence: float = DEFAULT_RELIABILITY_SCORE

    def __post_init__(self) -> None:
        _require_non_empty_text("span_id", self.span_id)
        _require_non_empty_text("post_id", self.post_id)
        _require_non_empty_text("field_name", self.field_name)
        _require_non_empty_text("text", self.text)
        _validate_non_negative_int("start_char", self.start_char)
        _validate_non_negative_int("end_char", self.end_char)
        if self.end_char <= self.start_char:
            raise ValueError("end_char must be greater than start_char.")
        _validate_score("confidence", self.confidence)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "EvidenceSpan":
        return cls(
            span_id=payload["span_id"],
            post_id=payload["post_id"],
            field_name=payload["field_name"],
            text=payload["text"],
            start_char=payload["start_char"],
            end_char=payload["end_char"],
            confidence=payload.get("confidence", DEFAULT_RELIABILITY_SCORE),
        )


@dataclass
class RawPost(SchemaModel):
    post_id: str
    source_type: SourceType
    source_url: Optional[str]
    author_id_masked: Optional[str]
    title: Optional[str]
    content_raw: str
    created_at: Optional[datetime]
    ingested_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("post_id", self.post_id)
        if not isinstance(self.source_type, SourceType):
            raise TypeError("source_type must be a SourceType.")
        _require_non_empty_text("content_raw", self.content_raw)
        if self.created_at is not None and not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime or None.")
        if not isinstance(self.ingested_at, datetime):
            raise TypeError("ingested_at must be a datetime.")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RawPost":
        return cls(
            post_id=payload["post_id"],
            source_type=SourceType(payload["source_type"]),
            source_url=payload.get("source_url"),
            author_id_masked=payload.get("author_id_masked"),
            title=payload.get("title"),
            content_raw=payload["content_raw"],
            created_at=_parse_datetime(payload.get("created_at")),
            ingested_at=_parse_datetime(payload["ingested_at"]),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass
class CleanedPost(SchemaModel):
    post_id: str
    content_cleaned: str
    segments: List[TextSegment]
    language: str = DEFAULT_LANGUAGE
    is_relevant: bool = True
    dedup_group_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("post_id", self.post_id)
        _require_non_empty_text("content_cleaned", self.content_cleaned)
        if not isinstance(self.segments, list):
            raise TypeError("segments must be a list.")
        for segment in self.segments:
            if not isinstance(segment, TextSegment):
                raise TypeError("segments must contain TextSegment items.")
        _require_non_empty_text("language", self.language)
        if not isinstance(self.is_relevant, bool):
            raise TypeError("is_relevant must be a bool.")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CleanedPost":
        return cls(
            post_id=payload["post_id"],
            content_cleaned=payload["content_cleaned"],
            segments=[TextSegment.from_dict(item) for item in payload.get("segments", [])],
            language=payload.get("language", DEFAULT_LANGUAGE),
            is_relevant=payload.get("is_relevant", True),
            dedup_group_id=payload.get("dedup_group_id"),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass
class InterviewRound(SchemaModel):
    round_id: str
    raw_label: str
    canonical_name: str
    stage_type: Optional[InterviewStageType] = None
    order_index: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("round_id", self.round_id)
        _require_non_empty_text("raw_label", self.raw_label)
        _require_non_empty_text("canonical_name", self.canonical_name)
        if self.stage_type is not None and not isinstance(self.stage_type, InterviewStageType):
            raise TypeError("stage_type must be an InterviewStageType or None.")
        if self.order_index is not None:
            _validate_non_negative_int("order_index", self.order_index)
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "InterviewRound":
        stage_type = _parse_enum(InterviewStageType, payload.get("stage_type"))
        return cls(
            round_id=payload["round_id"],
            raw_label=payload["raw_label"],
            canonical_name=payload["canonical_name"],
            stage_type=stage_type,
            order_index=payload.get("order_index"),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass
class InterviewEvent(SchemaModel):
    event_id: str
    post_id: str
    company: Optional[str]
    company_canonical: Optional[str]
    role: Optional[str]
    role_canonical: Optional[str]
    round: Optional[str]
    round_canonical: Optional[str]
    question_text: str
    answer_hint: Optional[str]
    topic_tags: List[str]
    difficulty_level: Optional[str]
    interview_stage_type: Optional[InterviewStageType]
    event_time: Optional[datetime]
    evidence_spans: List[EvidenceSpan]
    source_reliability_score: float = DEFAULT_RELIABILITY_SCORE
    question_type: Optional[QuestionType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("event_id", self.event_id)
        _require_non_empty_text("post_id", self.post_id)
        _require_non_empty_text("question_text", self.question_text)
        _validate_string_list("topic_tags", self.topic_tags)
        if self.interview_stage_type is not None and not isinstance(self.interview_stage_type, InterviewStageType):
            raise TypeError("interview_stage_type must be an InterviewStageType or None.")
        if self.event_time is not None and not isinstance(self.event_time, datetime):
            raise TypeError("event_time must be a datetime or None.")
        if not isinstance(self.evidence_spans, list):
            raise TypeError("evidence_spans must be a list.")
        for span in self.evidence_spans:
            if not isinstance(span, EvidenceSpan):
                raise TypeError("evidence_spans must contain EvidenceSpan items.")
        _validate_score("source_reliability_score", self.source_reliability_score)
        if self.question_type is not None and not isinstance(self.question_type, QuestionType):
            raise TypeError("question_type must be a QuestionType or None.")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "InterviewEvent":
        stage_type = _parse_enum(InterviewStageType, payload.get("interview_stage_type"))
        question_type = _parse_enum(QuestionType, payload.get("question_type"))
        return cls(
            event_id=payload["event_id"],
            post_id=payload["post_id"],
            company=payload.get("company"),
            company_canonical=payload.get("company_canonical"),
            role=payload.get("role"),
            role_canonical=payload.get("role_canonical"),
            round=payload.get("round"),
            round_canonical=payload.get("round_canonical"),
            question_text=payload["question_text"],
            answer_hint=payload.get("answer_hint"),
            topic_tags=list(payload.get("topic_tags", [])),
            difficulty_level=payload.get("difficulty_level"),
            interview_stage_type=stage_type,
            event_time=_parse_datetime(payload.get("event_time")),
            evidence_spans=[EvidenceSpan.from_dict(item) for item in payload.get("evidence_spans", [])],
            source_reliability_score=payload.get("source_reliability_score", DEFAULT_RELIABILITY_SCORE),
            question_type=question_type,
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass
class QuestionAtom(SchemaModel):
    question_id: str
    canonical_question: str
    normalized_question: str
    topic_tags: List[str]
    difficulty_level: Optional[str]
    question_type: Optional[QuestionType]
    source_event_ids: List[str]
    answer_hints: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _require_non_empty_text("question_id", self.question_id)
        _require_non_empty_text("canonical_question", self.canonical_question)
        _require_non_empty_text("normalized_question", self.normalized_question)
        _validate_string_list("topic_tags", self.topic_tags)
        _validate_string_list("source_event_ids", self.source_event_ids)
        _validate_string_list("answer_hints", self.answer_hints)
        if self.question_type is not None and not isinstance(self.question_type, QuestionType):
            raise TypeError("question_type must be a QuestionType or None.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "QuestionAtom":
        question_type = _parse_enum(QuestionType, payload.get("question_type"))
        return cls(
            question_id=payload["question_id"],
            canonical_question=payload["canonical_question"],
            normalized_question=payload["normalized_question"],
            topic_tags=list(payload.get("topic_tags", [])),
            difficulty_level=payload.get("difficulty_level"),
            question_type=question_type,
            source_event_ids=list(payload.get("source_event_ids", [])),
            answer_hints=list(payload.get("answer_hints", [])),
        )


@dataclass
class KnowledgeDocument(SchemaModel):
    document_id: str
    document_type: str
    title: str
    content: str
    question_ids: List[str]
    event_ids: List[str]
    topic_tags: List[str]
    created_at: datetime
    metadata_filters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("document_id", self.document_id)
        _require_non_empty_text("document_type", self.document_type)
        _require_non_empty_text("title", self.title)
        _require_non_empty_text("content", self.content)
        _validate_string_list("question_ids", self.question_ids)
        _validate_string_list("event_ids", self.event_ids)
        _validate_string_list("topic_tags", self.topic_tags)
        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")
        if not isinstance(self.metadata_filters, dict):
            raise TypeError("metadata_filters must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "KnowledgeDocument":
        return cls(
            document_id=payload["document_id"],
            document_type=payload["document_type"],
            title=payload["title"],
            content=payload["content"],
            question_ids=list(payload.get("question_ids", [])),
            event_ids=list(payload.get("event_ids", [])),
            topic_tags=list(payload.get("topic_tags", [])),
            created_at=_parse_datetime(payload["created_at"]),
            metadata_filters=dict(payload.get("metadata_filters", {})),
        )


@dataclass
class UserAttempt(SchemaModel):
    attempt_id: str
    user_id: str
    question_id: str
    session_id: str
    user_answer: str
    answer_duration_sec: int
    hint_used: bool
    submitted_at: datetime
    followup_used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("attempt_id", self.attempt_id)
        _require_non_empty_text("user_id", self.user_id)
        _require_non_empty_text("question_id", self.question_id)
        _require_non_empty_text("session_id", self.session_id)
        _require_non_empty_text("user_answer", self.user_answer)
        _validate_non_negative_int("answer_duration_sec", self.answer_duration_sec)
        if not isinstance(self.hint_used, bool):
            raise TypeError("hint_used must be a bool.")
        if not isinstance(self.submitted_at, datetime):
            raise TypeError("submitted_at must be a datetime.")
        if not isinstance(self.followup_used, bool):
            raise TypeError("followup_used must be a bool.")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UserAttempt":
        return cls(
            attempt_id=payload["attempt_id"],
            user_id=payload["user_id"],
            question_id=payload["question_id"],
            session_id=payload["session_id"],
            user_answer=payload["user_answer"],
            answer_duration_sec=payload["answer_duration_sec"],
            hint_used=payload["hint_used"],
            submitted_at=_parse_datetime(payload["submitted_at"]),
            followup_used=payload.get("followup_used", False),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass
class UserProfile(SchemaModel):
    user_id: str
    target_companies: List[str]
    target_roles: List[str]
    interview_goal: Optional[str]
    preferred_language: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("user_id", self.user_id)
        _validate_string_list("target_companies", self.target_companies)
        _validate_string_list("target_roles", self.target_roles)
        _require_non_empty_text("preferred_language", self.preferred_language)
        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")
        if not isinstance(self.updated_at, datetime):
            raise TypeError("updated_at must be a datetime.")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UserProfile":
        return cls(
            user_id=payload["user_id"],
            target_companies=list(payload.get("target_companies", [])),
            target_roles=list(payload.get("target_roles", [])),
            interview_goal=payload.get("interview_goal"),
            preferred_language=payload.get("preferred_language", DEFAULT_LANGUAGE),
            created_at=_parse_datetime(payload["created_at"]),
            updated_at=_parse_datetime(payload["updated_at"]),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass
class UserSkillState(SchemaModel):
    user_id: str
    topic: str
    correct_rate: float
    completeness_score: float
    depth_score: float
    communication_score: float
    followup_robustness_score: float
    forgetting_risk: float
    attempt_count: int
    last_practiced_at: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("user_id", self.user_id)
        _require_non_empty_text("topic", self.topic)
        _validate_score("correct_rate", self.correct_rate)
        _validate_score("completeness_score", self.completeness_score)
        _validate_score("depth_score", self.depth_score)
        _validate_score("communication_score", self.communication_score)
        _validate_score("followup_robustness_score", self.followup_robustness_score)
        _validate_score("forgetting_risk", self.forgetting_risk)
        _validate_non_negative_int("attempt_count", self.attempt_count)
        if self.last_practiced_at is not None and not isinstance(self.last_practiced_at, datetime):
            raise TypeError("last_practiced_at must be a datetime or None.")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UserSkillState":
        return cls(
            user_id=payload["user_id"],
            topic=payload["topic"],
            correct_rate=payload["correct_rate"],
            completeness_score=payload["completeness_score"],
            depth_score=payload["depth_score"],
            communication_score=payload["communication_score"],
            followup_robustness_score=payload["followup_robustness_score"],
            forgetting_risk=payload["forgetting_risk"],
            attempt_count=payload["attempt_count"],
            last_practiced_at=_parse_datetime(payload.get("last_practiced_at")),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass
class EvaluationResult(SchemaModel):
    evaluation_id: str
    attempt_id: str
    total_score: float
    correctness_score: float
    completeness_score: float
    depth_score: float
    communication_score: float
    followup_robustness_score: float
    strengths: List[str]
    weaknesses: List[str]
    missing_points: List[str]
    improvement_suggestions: List[str]
    recommended_topics: List[str]
    evaluated_at: datetime
    grader_version: str = "rule_based_v1"

    def __post_init__(self) -> None:
        _require_non_empty_text("evaluation_id", self.evaluation_id)
        _require_non_empty_text("attempt_id", self.attempt_id)
        _validate_score("total_score", self.total_score)
        _validate_score("correctness_score", self.correctness_score)
        _validate_score("completeness_score", self.completeness_score)
        _validate_score("depth_score", self.depth_score)
        _validate_score("communication_score", self.communication_score)
        _validate_score("followup_robustness_score", self.followup_robustness_score)
        _validate_string_list("strengths", self.strengths)
        _validate_string_list("weaknesses", self.weaknesses)
        _validate_string_list("missing_points", self.missing_points)
        _validate_string_list("improvement_suggestions", self.improvement_suggestions)
        _validate_string_list("recommended_topics", self.recommended_topics)
        if not isinstance(self.evaluated_at, datetime):
            raise TypeError("evaluated_at must be a datetime.")
        _require_non_empty_text("grader_version", self.grader_version)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "EvaluationResult":
        return cls(
            evaluation_id=payload["evaluation_id"],
            attempt_id=payload["attempt_id"],
            total_score=payload["total_score"],
            correctness_score=payload["correctness_score"],
            completeness_score=payload["completeness_score"],
            depth_score=payload["depth_score"],
            communication_score=payload["communication_score"],
            followup_robustness_score=payload["followup_robustness_score"],
            strengths=list(payload.get("strengths", [])),
            weaknesses=list(payload.get("weaknesses", [])),
            missing_points=list(payload.get("missing_points", [])),
            improvement_suggestions=list(payload.get("improvement_suggestions", [])),
            recommended_topics=list(payload.get("recommended_topics", [])),
            evaluated_at=_parse_datetime(payload["evaluated_at"]),
            grader_version=payload.get("grader_version", "rule_based_v1"),
        )


@dataclass
class QuestionRecommendation(SchemaModel):
    recommendation_id: str
    session_id: str
    question_id: str
    prompt_text: str
    target_relevance: float
    occurrence_confidence: float
    weakness_weight: float
    freshness_weight: float
    final_score: float
    rationale: List[str]
    recommended_followups: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _require_non_empty_text("recommendation_id", self.recommendation_id)
        _require_non_empty_text("session_id", self.session_id)
        _require_non_empty_text("question_id", self.question_id)
        _require_non_empty_text("prompt_text", self.prompt_text)
        _validate_score("target_relevance", self.target_relevance)
        _validate_score("occurrence_confidence", self.occurrence_confidence)
        _validate_score("weakness_weight", self.weakness_weight)
        _validate_score("freshness_weight", self.freshness_weight)
        _validate_score("final_score", self.final_score)
        _validate_string_list("rationale", self.rationale)
        _validate_string_list("recommended_followups", self.recommended_followups)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "QuestionRecommendation":
        return cls(
            recommendation_id=payload["recommendation_id"],
            session_id=payload["session_id"],
            question_id=payload["question_id"],
            prompt_text=payload["prompt_text"],
            target_relevance=payload["target_relevance"],
            occurrence_confidence=payload["occurrence_confidence"],
            weakness_weight=payload["weakness_weight"],
            freshness_weight=payload["freshness_weight"],
            final_score=payload["final_score"],
            rationale=list(payload.get("rationale", [])),
            recommended_followups=list(payload.get("recommended_followups", [])),
        )


@dataclass
class PracticePlanItem(SchemaModel):
    day_index: int
    topic: str
    objective: str
    question_count: int
    focus_reason: str

    def __post_init__(self) -> None:
        _validate_positive_int("day_index", self.day_index)
        _require_non_empty_text("topic", self.topic)
        _require_non_empty_text("objective", self.objective)
        _validate_positive_int("question_count", self.question_count)
        _require_non_empty_text("focus_reason", self.focus_reason)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PracticePlanItem":
        return cls(
            day_index=payload["day_index"],
            topic=payload["topic"],
            objective=payload["objective"],
            question_count=payload["question_count"],
            focus_reason=payload["focus_reason"],
        )


@dataclass
class PracticePlan(SchemaModel):
    plan_id: str
    user_id: str
    title: str
    goals: List[str]
    recommended_topics: List[str]
    daily_question_target: int
    horizon_days: int
    session_mode: SessionMode
    generated_at: datetime
    items: List[PracticePlanItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        _require_non_empty_text("plan_id", self.plan_id)
        _require_non_empty_text("user_id", self.user_id)
        _require_non_empty_text("title", self.title)
        _validate_string_list("goals", self.goals)
        _validate_string_list("recommended_topics", self.recommended_topics)
        _validate_positive_int("daily_question_target", self.daily_question_target)
        _validate_positive_int("horizon_days", self.horizon_days)
        if not isinstance(self.session_mode, SessionMode):
            raise TypeError("session_mode must be a SessionMode.")
        if not isinstance(self.generated_at, datetime):
            raise TypeError("generated_at must be a datetime.")
        if not isinstance(self.items, list):
            raise TypeError("items must be a list.")
        for item in self.items:
            if not isinstance(item, PracticePlanItem):
                raise TypeError("items must contain PracticePlanItem values.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PracticePlan":
        return cls(
            plan_id=payload["plan_id"],
            user_id=payload["user_id"],
            title=payload["title"],
            goals=list(payload.get("goals", [])),
            recommended_topics=list(payload.get("recommended_topics", [])),
            daily_question_target=payload["daily_question_target"],
            horizon_days=payload["horizon_days"],
            session_mode=SessionMode(payload["session_mode"]),
            generated_at=_parse_datetime(payload["generated_at"]),
            items=[PracticePlanItem.from_dict(item) for item in payload.get("items", [])],
        )


@dataclass
class PracticeSession(SchemaModel):
    session_id: str
    user_id: str
    mode: SessionMode
    target_company: Optional[str]
    target_role: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    status: SessionStatus = SessionStatus.CREATED
    planned_question_ids: List[str] = field(default_factory=list)
    completed_attempt_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_text("session_id", self.session_id)
        _require_non_empty_text("user_id", self.user_id)
        if not isinstance(self.mode, SessionMode):
            raise TypeError("mode must be a SessionMode.")
        if not isinstance(self.started_at, datetime):
            raise TypeError("started_at must be a datetime.")
        if self.ended_at is not None and not isinstance(self.ended_at, datetime):
            raise TypeError("ended_at must be a datetime or None.")
        if not isinstance(self.status, SessionStatus):
            raise TypeError("status must be a SessionStatus.")
        _validate_string_list("planned_question_ids", self.planned_question_ids)
        _validate_string_list("completed_attempt_ids", self.completed_attempt_ids)
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PracticeSession":
        return cls(
            session_id=payload["session_id"],
            user_id=payload["user_id"],
            mode=SessionMode(payload["mode"]),
            target_company=payload.get("target_company"),
            target_role=payload.get("target_role"),
            started_at=_parse_datetime(payload["started_at"]),
            ended_at=_parse_datetime(payload.get("ended_at")),
            status=SessionStatus(payload.get("status", SessionStatus.CREATED.value)),
            planned_question_ids=list(payload.get("planned_question_ids", [])),
            completed_attempt_ids=list(payload.get("completed_attempt_ids", [])),
            metadata=dict(payload.get("metadata", {})),
        )


SCHEMA_REGISTRY: Dict[str, Type[SchemaModel]] = {
    "RawPost": RawPost,
    "CleanedPost": CleanedPost,
    "InterviewEvent": InterviewEvent,
    "QuestionAtom": QuestionAtom,
    "EvidenceSpan": EvidenceSpan,
    "InterviewRound": InterviewRound,
    "KnowledgeDocument": KnowledgeDocument,
    "UserAttempt": UserAttempt,
    "UserProfile": UserProfile,
    "UserSkillState": UserSkillState,
    "EvaluationResult": EvaluationResult,
    "QuestionRecommendation": QuestionRecommendation,
    "PracticePlan": PracticePlan,
    "PracticeSession": PracticeSession,
}

__all__ = [
    "CleanedPost",
    "EvaluationResult",
    "EvidenceSpan",
    "InterviewEvent",
    "InterviewRound",
    "InterviewStageType",
    "KnowledgeDocument",
    "PracticePlan",
    "PracticePlanItem",
    "PracticeSession",
    "QuestionAtom",
    "QuestionRecommendation",
    "QuestionType",
    "RawPost",
    "SCHEMA_REGISTRY",
    "SchemaModel",
    "SessionMode",
    "SessionStatus",
    "SourceType",
    "TextSegment",
    "UserAttempt",
    "UserProfile",
    "UserSkillState",
]
