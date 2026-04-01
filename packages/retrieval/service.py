from .schemas import RetrievalRequest, RetrievalResult


class RetrievalService:
    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """TODO: implement hybrid retrieval and ranking."""

        _ = request
        return RetrievalResult()
