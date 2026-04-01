from .schemas import ExtractionRequest, ExtractionResult


class ExtractionService:
    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """TODO: implement the extraction pipeline."""

        _ = request
        return ExtractionResult()
