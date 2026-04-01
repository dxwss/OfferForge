import unittest

from packages.taxonomy.schemas import TaxonomyResolutionRequest
from packages.taxonomy.service import TaxonomyService


class TaxonomyServiceSmokeTest(unittest.TestCase):
    def test_resolve_returns_result_object(self) -> None:
        service = TaxonomyService()
        result = service.resolve(TaxonomyResolutionRequest(events=[]))

        self.assertEqual(result.resolved_events, [])
        self.assertEqual(result.applied_rules, [])


if __name__ == "__main__":
    unittest.main()
