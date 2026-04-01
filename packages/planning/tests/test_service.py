import unittest

from packages.planning.schemas import PlanningRequest
from packages.planning.service import PlanningService


class PlanningServiceSmokeTest(unittest.TestCase):
    def test_plan_returns_result_object(self) -> None:
        service = PlanningService()
        result = service.plan(PlanningRequest())

        self.assertIsNone(result.recommendation)
        self.assertIsNone(result.practice_plan)


if __name__ == "__main__":
    unittest.main()
