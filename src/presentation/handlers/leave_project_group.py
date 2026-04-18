from pydantic import UUID4

from application.compositions import LeaveProjectGroupComposition
from application.usecases import LeaveProjectGroupRequest


class LeaveProjectGroupHandler:
    def __init__(self, usecase: LeaveProjectGroupComposition):
        self._usecase = usecase

    async def __call__(
        self,
        project_id: UUID4,
        group_id: UUID4,
        participant_id: UUID4,
    ) -> None:
        await self._usecase(
            LeaveProjectGroupRequest.from_primitives(
                project_id=str(project_id),
                group_id=str(group_id),
                participant_id=str(participant_id),
            )
        )
