from typing import Protocol

from .schemas import KnowledgeBuildRequest, KnowledgeBuildResult


class KnowledgeBuilderServiceProtocol(Protocol):
    def build(self, request: KnowledgeBuildRequest) -> KnowledgeBuildResult:
        ...
