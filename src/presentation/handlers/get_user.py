from pydantic import UUID4


from application.compositions import GetUserCompostion
from application.usecases.get_user import GetUserRequest, GetUserResponse
from presentation.models.user import UserRead


class GetUserHandler:

    def __init__(self, usecase: GetUserCompostion):
        self._usecase = usecase

    async def __call__(self, user_id: UUID4) -> GetUserResponse:

        response: GetUserResponse = await self._usecase(
            GetUserRequest.from_primitives(str(user_id))
        )
        return UserRead(
            name=response["name"],
            bio=response["bio"],
            birthdate=response["birthdate"],
        )
