import unittest

from packages.knowledge_builder.schemas import KnowledgeBuildRequest
from packages.knowledge_builder.service import KnowledgeBuilderService


class KnowledgeBuilderServiceSmokeTest(unittest.TestCase):
    def test_build_returns_result_object(self) -> None:
        service = KnowledgeBuilderService()
        result = service.build(KnowledgeBuildRequest(events=[]))

        self.assertEqual(result.question_atoms, [])
        self.assertEqual(result.knowledge_documents, [])


if __name__ == "__main__":
    unittest.main()
