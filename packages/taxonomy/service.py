from .schemas import TaxonomyResolutionRequest, TaxonomyResolutionResult


class TaxonomyService:
    def resolve(self, request: TaxonomyResolutionRequest) -> TaxonomyResolutionResult:
        """TODO: implement taxonomy rules and entity resolution."""

        return TaxonomyResolutionResult(resolved_events=list(request.events))
