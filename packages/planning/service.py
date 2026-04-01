from .schemas import PlanningRequest, PlanningResult


class PlanningService:
    def plan(self, request: PlanningRequest) -> PlanningResult:
        """TODO: implement recommendation scoring and study planning."""

        _ = request
        return PlanningResult()
