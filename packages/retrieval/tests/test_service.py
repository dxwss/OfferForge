import unittest

from packages.retrieval.schemas import RetrievalRequest
from packages.retrieval.service import RetrievalService


class RetrievalServiceSmokeTest(unittest.TestCase):
    def test_retrieve_returns_result_object(self) -> None:
        service = RetrievalService()
        result = service.retrieve(RetrievalRequest())

        self.assertEqual(result.candidate_questions, [])
        self.assertEqual(result.evidence_documents, [])


if __name__ == "__main__":
    unittest.main()
