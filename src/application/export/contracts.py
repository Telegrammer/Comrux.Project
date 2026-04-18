from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Sequence

from domain.entities.project import ProjectId
from domain.export import ProjectRelease, ProjectReleaseId, ProjectReleaseStatus


@dataclass(frozen=True)
class ProjectTreeNodeSnapshot:
    path: str
    unit_type: str
    content_ref: str | None = None


@dataclass(frozen=True)
class PublishedGroupContent:
    content_id: str
    content: bytes


@dataclass(frozen=True)
class StoredProjectReleaseArtifact:
    artifact_key: str
    file_name: str
    archive_size: int


@dataclass(frozen=True)
class ProjectReleaseDownload:
    file_name: str
    media_type: str
    content: bytes


class ProjectReleaseCommandGateway(Protocol):
    async def add(self, release: ProjectRelease) -> None: ...

    async def update(self, release: ProjectRelease) -> None: ...


class ProjectReleaseQueryGateway(Protocol):
    async def by_id(self, release_id: ProjectReleaseId) -> ProjectRelease | None: ...

    async def list_by_project(
        self,
        project_id: ProjectId,
        status: ProjectReleaseStatus,
        limit: int,
        offset: int,
    ) -> tuple[list[ProjectRelease], int]: ...


class ProjectTreeSnapshotGateway(Protocol):
    async def by_project(self, project_id: ProjectId) -> Sequence[ProjectTreeNodeSnapshot]: ...


class GroupPublishedContentGateway(Protocol):
    async def by_group(self, group_id: ProjectId) -> Sequence[PublishedGroupContent]: ...


class ProjectReleaseArtifactGateway(Protocol):
    async def build_and_store(
        self,
        release: ProjectRelease,
        tree: Sequence[ProjectTreeNodeSnapshot],
        contents: Sequence[PublishedGroupContent],
        finished_at: datetime,
    ) -> StoredProjectReleaseArtifact: ...

    async def download(
        self,
        release: ProjectRelease,
    ) -> ProjectReleaseDownload: ...
