import unittest
from datetime import datetime, timezone

from packages.shared_schema.schema import (
    EvaluationResult,
    EvidenceSpan,
    InterviewEvent,
    InterviewStageType,
    PracticePlan,
    PracticePlanItem,
    PracticeSession,
    QuestionType,
    RawPost,
    SessionMode,
    SessionStatus,
    SourceType,
    TextSegment,
    UserSkillState,
)
from packages.shared_schema.service import SharedSchemaService


class SharedSchemaServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SharedSchemaService()
        self.now = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)

    def test_registry_contains_core_models(self) -> None:
        models = list(self.service.list_models())
        self.assertIn("RawPost", models)
        self.assertIn("InterviewEvent", models)
        self.assertIn("PracticeSession", models)

    def test_raw_post_round_trip(self) -> None:
        raw_post = RawPost(
            post_id="post_001",
            source_type=SourceType.MANUAL_IMPORT,
            source_url="https://example.com/post/1",
            author_id_masked="user_xxx",
            title="字节后端一面面经",
            content_raw="问了 TCP 三次握手、Redis 持久化和 MySQL 索引。",
            created_at=self.now,
            ingested_at=self.now,
            metadata={"lang": "zh"},
        )

        payload = self.service.serialize(raw_post)
        rebuilt = self.service.deserialize("RawPost", payload)

        self.assertEqual(rebuilt, raw_post)
        self.assertEqual(payload["source_type"], "manual_import")

    def test_interview_event_round_trip_with_nested_evidence(self) -> None:
        event = InterviewEvent(
            event_id="event_001",
            post_id="post_001",
            company="字节",
            company_canonical="bytedance",
            role="后端实习",
            role_canonical="backend_intern",
            round="一面",
            round_canonical="technical_round_1",
            question_text="解释 TCP 三次握手为什么不是两次。",
            answer_hint="从可靠建立连接和历史报文干扰角度说明。",
            topic_tags=["network", "tcp"],
            difficulty_level="medium",
            interview_stage_type=InterviewStageType.TECHNICAL,
            event_time=self.now,
            evidence_spans=[
                EvidenceSpan(
                    span_id="span_001",
                    post_id="post_001",
                    field_name="question_text",
                    text="问了 TCP 三次握手为什么不是两次",
                    start_char=0,
                    end_char=18,
                    confidence=0.9,
                )
            ],
            source_reliability_score=0.8,
            question_type=QuestionType.KNOWLEDGE,
            metadata={"source": "manual_label"},
        )

        payload = self.service.serialize(event)
        rebuilt = self.service.deserialize("InterviewEvent", payload)

        self.assertEqual(rebuilt, event)
        self.assertEqual(payload["interview_stage_type"], "technical")
        self.assertEqual(payload["evidence_spans"][0]["confidence"], 0.9)

    def test_practice_plan_and_session_round_trip(self) -> None:
        plan = PracticePlan(
            plan_id="plan_001",
            user_id="user_001",
            title="7 天后端冲刺",
            goals=["补齐网络和数据库高频题"],
            recommended_topics=["network", "database"],
            daily_question_target=8,
            horizon_days=7,
            session_mode=SessionMode.PRACTICE,
            generated_at=self.now,
            items=[
                PracticePlanItem(
                    day_index=1,
                    topic="network",
                    objective="补齐 TCP 和 HTTP 高频题",
                    question_count=8,
                    focus_reason="当前网络题正确率偏低",
                )
            ],
        )
        session = PracticeSession(
            session_id="session_001",
            user_id="user_001",
            mode=SessionMode.MOCK_INTERVIEW,
            target_company="bytedance",
            target_role="backend_intern",
            started_at=self.now,
            ended_at=None,
            status=SessionStatus.ACTIVE,
            planned_question_ids=["q_001", "q_002"],
            completed_attempt_ids=["attempt_001"],
            metadata={"difficulty": "medium"},
        )

        rebuilt_plan = self.service.deserialize("PracticePlan", self.service.serialize(plan))
        rebuilt_session = self.service.deserialize("PracticeSession", self.service.serialize(session))

        self.assertEqual(rebuilt_plan, plan)
        self.assertEqual(rebuilt_session, session)

    def test_invalid_score_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            UserSkillState(
                user_id="user_001",
                topic="network",
                correct_rate=1.2,
                completeness_score=0.5,
                depth_score=0.5,
                communication_score=0.5,
                followup_robustness_score=0.5,
                forgetting_risk=0.5,
                attempt_count=3,
                last_practiced_at=self.now,
            )

    def test_evaluation_result_validates_dimension_scores(self) -> None:
        result = EvaluationResult(
            evaluation_id="eval_001",
            attempt_id="attempt_001",
            total_score=0.7,
            correctness_score=0.8,
            completeness_score=0.7,
            depth_score=0.6,
            communication_score=0.8,
            followup_robustness_score=0.5,
            strengths=["结构清晰"],
            weaknesses=["遗漏了拥塞控制"],
            missing_points=["没有解释 TIME_WAIT"],
            improvement_suggestions=["补充连接释放和 TIME_WAIT 的意义"],
            recommended_topics=["network"],
            evaluated_at=self.now,
        )

        payload = self.service.serialize(result)
        rebuilt = self.service.deserialize("EvaluationResult", payload)

        self.assertEqual(rebuilt, result)

    def test_cleaned_post_segments_require_valid_ranges(self) -> None:
        with self.assertRaises(ValueError):
            TextSegment(
                text="一面先问了项目，再问了 Redis。",
                start_char=20,
                end_char=10,
            )


if __name__ == "__main__":
    unittest.main()
