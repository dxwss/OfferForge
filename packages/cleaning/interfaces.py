from typing import Protocol

from .schemas import CleaningRequest, CleaningResult


class CleaningServiceProtocol(Protocol):
    def clean(self, request: CleaningRequest) -> CleaningResult:
        ...
