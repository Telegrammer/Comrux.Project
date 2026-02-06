from application.compositions import GrantOwnerComposition
from presentation.models import ProjectGrantOwner, ProjectOwnerGranted
from application.usecases import GrantOwnerRequest, GrantOwnerResponse


class GrantOwnerHandler:

    def __init__(self, usecase: GrantOwnerComposition):
        self._usecase = usecase

    async def __call__(
        self, project_id: str, request: ProjectGrantOwner
    ) -> ProjectOwnerGranted:

        response: GrantOwnerResponse = await self._usecase(
            GrantOwnerRequest.from_primitives(str(request.user), str(project_id))
        )

        return ProjectOwnerGranted(
            old_owner=response["old_owner_name"],
            new_role=response["old_owner_role"],
            project=response["project"],
        )
