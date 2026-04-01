from typing import Protocol

from .schemas import AssessmentRequest, AssessmentResultBundle


class AssessmentServiceProtocol(Protocol):
    def assess(self, request: AssessmentRequest) -> AssessmentResultBundle:
        ...
