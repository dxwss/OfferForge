from .schemas import KnowledgeBuildRequest, KnowledgeBuildResult


class KnowledgeBuilderService:
    def build(self, request: KnowledgeBuildRequest) -> KnowledgeBuildResult:
        """TODO: implement question atom and document building."""

        _ = request
        return KnowledgeBuildResult()
