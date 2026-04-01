from typing import Protocol

from .schemas import ApiResponse, StartSessionRequest, SubmitAnswerRequest


class ApiServiceProtocol(Protocol):
    def start_session(self, request: StartSessionRequest) -> ApiResponse:
        ...

    def submit_answer(self, request: SubmitAnswerRequest) -> ApiResponse:
        ...

    def get_practice_plan(self, user_id: str) -> ApiResponse:
        ...
