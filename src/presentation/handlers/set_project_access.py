from application.usecases import SetProjectAccessRequest
from application.compositions import SetProjectAccessComposition


class SetProjectAccessHandler:

    def __init__(self, usecase: SetProjectAccessComposition):
        self._usecase = usecase

    async def __call__(self, project_id: str, is_private: bool) -> None:
        await self._usecase(
            SetProjectAccessRequest.from_primitives(
                project_id,
                is_private,
            )
        )
