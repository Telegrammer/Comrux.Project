from application.usecases import GetUserUsecase, GetUserRequest, GetUserResponse
import logging

logger = logging.getLogger(__name__)


class GetUserCompostion:

    def __init__(self, usecase: GetUserUsecase):
        self._usecase = usecase

    async def __call__(self, request: GetUserRequest) -> GetUserResponse:

        logger.info("Fetching user %s:", request.user_id.value)
        response: GetUserResponse = await self._usecase(request)
        logger.info("Successfully fetched user")
        return response
