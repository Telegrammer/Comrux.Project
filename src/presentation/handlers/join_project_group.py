from pydantic import UUID4

from application.compositions import JoinProjectGroupComposition
from application.usecases import JoinProjectGroupRequest
from presentation.models import ProjectGroupJoin


class JoinProjectGroupHandler:
    def __init__(self, usecase: JoinProjectGroupComposition):
        self._usecase = usecase

    async def __call__(
        self,
        project_id: UUID4,
        group_id: UUID4,
        request_body: ProjectGroupJoin,
    ) -> None:
        await self._usecase(
            JoinProjectGroupRequest.from_primitives(
                project_id=str(project_id),
                group_id=str(group_id),
                participant_id=str(request_body.participant_id),
            )
        )
