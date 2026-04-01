from typing import Protocol

from .schemas import UserModelingRequest, UserModelingResult


class UserModelingServiceProtocol(Protocol):
    def update(self, request: UserModelingRequest) -> UserModelingResult:
        ...
