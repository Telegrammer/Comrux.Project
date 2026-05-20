from pydantic import UUID4

from application.compositions import SetProjectTaskStatusComposition
from application.usecases import SetProjectTaskStatusRequest, SetProjectTaskStatusResponse
from domain.enums import ProjectTaskStatus
from presentation.models import ProjectTaskSetStatus, ProjectTaskStatusChanged


class SetProjectTaskStatusHandler:
    def __init__(self, usecase: SetProjectTaskStatusComposition):
        self._usecase = usecase

    async def __call__(
        self, task_id: UUID4, request_body: ProjectTaskSetStatus
    ) -> ProjectTaskStatusChanged:
        target_status = (
            ProjectTaskStatus.DONE
            if request_body.status == "complete"
            else ProjectTaskStatus.CANCELED
        )
        response: SetProjectTaskStatusResponse = await self._usecase(
            SetProjectTaskStatusRequest.from_primitives(
                str(task_id), target_status.value
            )
        )
        return ProjectTaskStatusChanged(
            task_id=response["task_id"],
            status=response["status"],
        )
