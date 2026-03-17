from application.usecases import GetCurrentUserUsecase, GetCurrentUserResponse
from presentation.models.user import UserRead


class GetCurrentUserHandler:

    def __init__(self, usecase: GetCurrentUserUsecase):
        self._usecase = usecase

    async def __call__(self) -> GetCurrentUserResponse:

        response: GetCurrentUserResponse = await self._usecase()
        return UserRead(
            name=response["name"],
            bio=response["bio"],
            birthdate=response["birthdate"],
        )
