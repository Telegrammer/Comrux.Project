from pydantic import UUID4

from application.export import (
    CreateProjectReleaseComposition,
    CreateProjectReleaseRequest,
    DownloadProjectReleaseRequest,
    DownloadProjectReleaseUsecase,
    GetProjectReleaseRequest,
    GetProjectReleaseUsecase,
)
from application.export.contracts import ProjectReleaseArtifactGateway, ProjectReleaseDownload
from presentation.export.models import (
    ProjectReleaseCreate,
    ProjectReleaseCreatedResponse,
    ProjectReleaseReadResponse,
)
from utils import unwrap_value


class CreateProjectReleaseHandler:
    def __init__(self, usecase: CreateProjectReleaseComposition) -> None:
        self._usecase = usecase

    async def __call__(
        self,
        project_id: UUID4,
        request: ProjectReleaseCreate,
    ) -> ProjectReleaseCreatedResponse:
        release = await self._usecase(
            CreateProjectReleaseRequest.from_primitives(
                project_id=str(project_id),
                name=request.name,
            )
        )
        return ProjectReleaseCreatedResponse(
            release_id=str(unwrap_value(release.id_)),
            project_id=str(unwrap_value(release.project_id)),
            status=release.status.value,
            name=release.name,
        )


class GetProjectReleaseHandler:
    def __init__(self, usecase: GetProjectReleaseUsecase) -> None:
        self._usecase = usecase

    async def __call__(
        self, project_id: UUID4, release_id: UUID4
    ) -> ProjectReleaseReadResponse:
        response = await self._usecase(
            GetProjectReleaseRequest.from_primitives(
                project_id=str(project_id),
                release_id=str(release_id),
            )
        )
        return ProjectReleaseReadResponse.model_validate(response)


class DownloadProjectReleaseHandler:
    def __init__(
        self,
        usecase: DownloadProjectReleaseUsecase,
        artifacts: ProjectReleaseArtifactGateway,
    ) -> None:
        self._usecase = usecase
        self._artifacts = artifacts

    async def __call__(
        self,
        project_id: UUID4,
        release_id: UUID4,
    ) -> ProjectReleaseDownload:
        return await self._usecase(
            DownloadProjectReleaseRequest.from_primitives(
                project_id=str(project_id),
                release_id=str(release_id),
            ),
            self._artifacts,
        )
