from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from application.exceptions import (
    AccessDeniedError,
    ProjectNotFoundError,
    ProjectReleaseNotFoundError,
    ProjectReleaseNotReadyError,
)
from application.export.contracts import (
    ProjectReleaseDownload,
    ProjectReleaseQueryGateway,
)
from application.services import CurrentUserService
from domain.entities.project import Project, ProjectId
from domain.entities.user import User, UserId
from domain.export import (
    ProjectRelease,
    ProjectReleaseId,
    ProjectReleaseService,
    ProjectReleaseStatus,
)
from application.ports import Clock, ProjectQueryGateway
from utils import unwrap_value


class ProjectReleaseReadResult(TypedDict):
    id_: str
    project_id: str
    name: str
    status: str
    file_name: str | None
    archive_size: int | None
    error_message: str | None
    created_at: str
    started_at: str | None
    finished_at: str | None


@dataclass(frozen=True)
class CreateProjectReleaseRequest:
    project_id: ProjectId
    name: str

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        name: str,
    ) -> "CreateProjectReleaseRequest":
        return cls(project_id=ProjectId(project_id), name=name)


@dataclass(frozen=True)
class GetProjectReleaseRequest:
    project_id: ProjectId
    release_id: ProjectReleaseId

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        release_id: str,
    ) -> "GetProjectReleaseRequest":
        return cls(
            project_id=ProjectId(project_id),
            release_id=ProjectReleaseId(release_id),
        )


@dataclass(frozen=True)
class DownloadProjectReleaseRequest:
    project_id: ProjectId
    release_id: ProjectReleaseId

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        release_id: str,
    ) -> "DownloadProjectReleaseRequest":
        return cls(
            project_id=ProjectId(project_id),
            release_id=ProjectReleaseId(release_id),
        )


class CreateProjectReleaseUsecase:
    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        release_service: ProjectReleaseService,
        clock: Clock,
    ) -> None:
        self._current_user = current_user
        self._project_queries = project_queries
        self._release_service = release_service
        self._clock = clock

    async def __call__(
        self,
        request: CreateProjectReleaseRequest,
    ) -> ProjectRelease:
        project: Project = await self._project_queries.by_id(request.project_id)
        current_user: User = await self._current_user()

        if UserId(str(unwrap_value(current_user.id_))) not in project.members:
            raise AccessDeniedError("Only project members can create releases")

        return self._release_service.create_release(
            project_id=ProjectId(unwrap_value(project.id_)),
            requested_by=UserId(unwrap_value(current_user.id_)),
            name=request.name,
            now=self._clock.now(),
        )


class GetProjectReleaseUsecase:
    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        release_queries: ProjectReleaseQueryGateway,
    ) -> None:
        self._current_user = current_user
        self._project_queries = project_queries
        self._release_queries = release_queries

    async def __call__(self, request: GetProjectReleaseRequest) -> ProjectReleaseReadResult:
        project: Project = await self._project_queries.by_id(request.project_id)
        current_user: User = await self._current_user()

        if UserId(str(unwrap_value(current_user.id_))) not in project.members:
            raise AccessDeniedError("Only project members can read releases")

        release = await self._release_queries.by_id(request.release_id)
        if release is None or unwrap_value(release.project_id) != unwrap_value(project.id_):
            raise ProjectReleaseNotFoundError(
                "Release does not belong to the given project"
            )

        return ProjectReleaseReadResult(
            id_=str(unwrap_value(release.id_)),
            project_id=str(unwrap_value(release.project_id)),
            name=release.name,
            status=release.status.value,
            file_name=release.file_name,
            archive_size=release.archive_size,
            error_message=release.error_message,
            created_at=unwrap_value(release.created_at).isoformat(),
            started_at=(
                release.started_at.isoformat() if release.started_at is not None else None
            ),
            finished_at=(
                release.finished_at.isoformat()
                if release.finished_at is not None
                else None
            ),
        )


class DownloadProjectReleaseUsecase:
    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        release_queries: ProjectReleaseQueryGateway,
    ) -> None:
        self._current_user = current_user
        self._project_queries = project_queries
        self._release_queries = release_queries

    async def load_release(
        self,
        request: DownloadProjectReleaseRequest,
    ) -> ProjectRelease:
        project: Project = await self._project_queries.by_id(request.project_id)
        current_user: User = await self._current_user()

        if UserId(str(unwrap_value(current_user.id_))) not in project.members:
            raise AccessDeniedError("Only project members can download releases")

        release = await self._release_queries.by_id(request.release_id)
        if release is None or unwrap_value(release.project_id) != unwrap_value(project.id_):
            raise ProjectReleaseNotFoundError(
                "Release does not belong to the given project"
            )
        if release.status is not ProjectReleaseStatus.READY:
            raise ProjectReleaseNotReadyError("Release archive is not ready yet")
        return release

    async def __call__(
        self,
        request: DownloadProjectReleaseRequest,
        artifacts,
    ) -> ProjectReleaseDownload:
        release = await self.load_release(request)
        return await artifacts.download(release)
