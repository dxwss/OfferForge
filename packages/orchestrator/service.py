from .schemas import OrchestrationRequest, OrchestrationResult


class OrchestratorService:
    def step(self, request: OrchestrationRequest) -> OrchestrationResult:
        """TODO: implement session orchestration and state transitions."""

        return OrchestrationResult(session=request.session)
