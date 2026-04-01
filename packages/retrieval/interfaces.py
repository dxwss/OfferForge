from typing import Protocol

from .schemas import RetrievalRequest, RetrievalResult


class RetrievalServiceProtocol(Protocol):
    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        ...
