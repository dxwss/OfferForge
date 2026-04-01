from .schemas import ApiResponse, StartSessionRequest, SubmitAnswerRequest


class ApiService:
    def start_session(self, request: StartSessionRequest) -> ApiResponse:
        """TODO: connect session startup to the orchestrator."""

        _ = request
        return ApiResponse(message="start_session TODO")

    def submit_answer(self, request: SubmitAnswerRequest) -> ApiResponse:
        """TODO: connect answer submission to assessment and user modeling."""

        _ = request
        return ApiResponse(message="submit_answer TODO")

    def get_practice_plan(self, user_id: str) -> ApiResponse:
        """TODO: connect plan retrieval to the planning module."""

        _ = user_id
        return ApiResponse(message="get_practice_plan TODO")
