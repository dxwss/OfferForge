import unittest
from datetime import datetime, timezone

from packages.assessment.schemas import AssessmentRequest
from packages.assessment.service import AssessmentService
from packages.shared_schema import SessionMode, SessionStatus, PracticeSession, UserAttempt


class AssessmentServiceSmokeTest(unittest.TestCase):
    def test_assess_returns_result_object(self) -> None:
        now = datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc)
        _ = PracticeSession(
            session_id="session_001",
            user_id="user_001",
            mode=SessionMode.PRACTICE,
            target_company=None,
            target_role=None,
            started_at=now,
            ended_at=None,
            status=SessionStatus.ACTIVE,
        )
        attempt = UserAttempt(
            attempt_id="attempt_001",
            user_id="user_001",
            question_id="question_001",
            session_id="session_001",
            user_answer="placeholder answer",
            answer_duration_sec=30,
            hint_used=False,
            submitted_at=now,
        )

        service = AssessmentService()
        result = service.assess(AssessmentRequest(attempt=attempt))

        self.assertIsNone(result.evaluation)
        self.assertEqual(result.followup_topics, [])


if __name__ == "__main__":
    unittest.main()
