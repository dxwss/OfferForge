from typing import Protocol

from .schemas import PlanningRequest, PlanningResult


class PlanningServiceProtocol(Protocol):
    def plan(self, request: PlanningRequest) -> PlanningResult:
        ...
