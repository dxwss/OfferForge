from .schemas import UserModelingRequest, UserModelingResult


class UserModelingService:
    def update(self, request: UserModelingRequest) -> UserModelingResult:
        """TODO: implement skill-state and memory updates."""

        return UserModelingResult(profile=request.profile)
