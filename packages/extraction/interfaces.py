from typing import Protocol

from .schemas import ExtractionRequest, ExtractionResult


class ExtractionServiceProtocol(Protocol):
    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        ...
