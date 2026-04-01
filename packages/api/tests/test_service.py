import unittest

from packages.api.schemas import StartSessionRequest, SubmitAnswerRequest
from packages.api.service import ApiService


class ApiServiceSmokeTest(unittest.TestCase):
    def test_api_methods_return_response_objects(self) -> None:
        service = ApiService()

        start_response = service.start_session(StartSessionRequest(user_id="user_001"))
        submit_response = service.submit_answer(
            SubmitAnswerRequest(
                user_id="user_001",
                session_id="session_001",
                question_id="question_001",
                answer="placeholder answer",
            )
        )

        self.assertTrue(start_response.success)
        self.assertTrue(submit_response.success)


if __name__ == "__main__":
    unittest.main()
