from .schemas import AssessmentRequest, AssessmentResultBundle


class AssessmentService:
    def assess(self, request: AssessmentRequest) -> AssessmentResultBundle:
        """TODO: implement grading rubrics and feedback generation."""

        _ = request
        return AssessmentResultBundle()
