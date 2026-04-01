from typing import Protocol

from .schemas import OrchestrationRequest, OrchestrationResult


class OrchestratorServiceProtocol(Protocol):
    def step(self, request: OrchestrationRequest) -> OrchestrationResult:
        ...
