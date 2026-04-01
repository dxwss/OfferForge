from typing import Protocol

from .schemas import TaxonomyResolutionRequest, TaxonomyResolutionResult


class TaxonomyServiceProtocol(Protocol):
    def resolve(self, request: TaxonomyResolutionRequest) -> TaxonomyResolutionResult:
        ...
