__all__ = ["CreatUserHandler"]


from application.usecases import CreateUserRequest
from application.compositions import CreateUserComposition
from presentation.models import UserCreate, UserCreated


class CreateUserHandler:

    def __init__(self, usecase: CreateUserComposition):
        self._usecase: CreateUserComposition = usecase

    async def __call__(self, request: UserCreate) -> UserCreated:
        return await self._usecase(
            CreateUserRequest.from_primitives(**request.model_dump())
        )
