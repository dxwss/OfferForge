import unittest

from packages.user_modeling.schemas import UserModelingRequest
from packages.user_modeling.service import UserModelingService


class UserModelingServiceSmokeTest(unittest.TestCase):
    def test_update_returns_result_object(self) -> None:
        service = UserModelingService()
        result = service.update(UserModelingRequest())

        self.assertIsNone(result.profile)
        self.assertEqual(result.skill_states, [])


if __name__ == "__main__":
    unittest.main()
