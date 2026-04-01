import unittest

from packages.extraction.schemas import ExtractionRequest
from packages.extraction.service import ExtractionService


class ExtractionServiceSmokeTest(unittest.TestCase):
    def test_extract_returns_result_object(self) -> None:
        service = ExtractionService()
        result = service.extract(ExtractionRequest(cleaned_posts=[]))

        self.assertEqual(result.events, [])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()
