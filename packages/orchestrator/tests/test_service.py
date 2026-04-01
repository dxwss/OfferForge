import unittest

from packages.orchestrator.schemas import OrchestrationRequest
from packages.orchestrator.service import OrchestratorService


class OrchestratorServiceSmokeTest(unittest.TestCase):
    def test_step_returns_result_object(self) -> None:
        service = OrchestratorService()
        result = service.step(OrchestrationRequest(user_id="user_001"))

        self.assertEqual(result.next_action, "noop")
        self.assertIsNone(result.session)


if __name__ == "__main__":
    unittest.main()
