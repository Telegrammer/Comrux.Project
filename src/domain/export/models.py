from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from domain.exceptions import DomainFieldError
from domain.entities.base import AggregationRoot
from domain.entities.project import ProjectId
from domain.entities.user import UserId
from domain.value_objects import PassedDatetime, Uuid4
from utils import unwrap_value

if TYPE_CHECKING:
    from .ports import ProjectReleaseIdGenerator


class ProjectReleaseId(Uuid4): ...


class ProjectReleaseStatus(StrEnum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


@dataclass(kw_only=True)
class ProjectRelease(AggregationRoot[ProjectReleaseId]):
    project_id: ProjectId
    requested_by: UserId
    name: str
    status: ProjectReleaseStatus
    artifact_key: str | None
    file_name: str | None
    archive_size: int | None
    error_message: str | None
    created_at: PassedDatetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ProjectReleaseService:
    def __init__(self, id_generator: "ProjectReleaseIdGenerator") -> None:
        self._id_generator = id_generator

    def create_release(
        self,
        project_id: ProjectId,
        requested_by: UserId,
        name: str,
        now: datetime,
    ) -> ProjectRelease:
        normalized_name = name.strip()
        if normalized_name == "":
            raise DomainFieldError("Release name must not be empty")

        return ProjectRelease(
            id_=self._id_generator(),
            project_id=project_id,
            requested_by=requested_by,
            name=normalized_name,
            status=ProjectReleaseStatus.CREATED,
            artifact_key=None,
            file_name=None,
            archive_size=None,
            error_message=None,
            created_at=PassedDatetime(now, now),
        )

    def mark_processing(
        self,
        release: ProjectRelease,
        now: datetime,
    ) -> ProjectRelease:
        return ProjectRelease(
            id_=ProjectReleaseId(unwrap_value(release.id_)),
            project_id=ProjectId(unwrap_value(release.project_id)),
            requested_by=UserId(unwrap_value(release.requested_by)),
            name=release.name,
            status=ProjectReleaseStatus.PROCESSING,
            artifact_key=release.artifact_key,
            file_name=release.file_name,
            archive_size=release.archive_size,
            error_message=None,
            created_at=PassedDatetime(unwrap_value(release.created_at), now),
            started_at=now,
            finished_at=None,
        )

    def mark_ready(
        self,
        release: ProjectRelease,
        artifact_key: str,
        file_name: str,
        archive_size: int,
        now: datetime,
    ) -> ProjectRelease:
        return ProjectRelease(
            id_=ProjectReleaseId(unwrap_value(release.id_)),
            project_id=ProjectId(unwrap_value(release.project_id)),
            requested_by=UserId(unwrap_value(release.requested_by)),
            name=release.name,
            status=ProjectReleaseStatus.READY,
            artifact_key=artifact_key,
            file_name=file_name,
            archive_size=archive_size,
            error_message=None,
            created_at=PassedDatetime(unwrap_value(release.created_at), now),
            started_at=release.started_at,
            finished_at=now,
        )

    def mark_failed(
        self,
        release: ProjectRelease,
        error_message: str,
        now: datetime,
    ) -> ProjectRelease:
        return ProjectRelease(
            id_=ProjectReleaseId(unwrap_value(release.id_)),
            project_id=ProjectId(unwrap_value(release.project_id)),
            requested_by=UserId(unwrap_value(release.requested_by)),
            name=release.name,
            status=ProjectReleaseStatus.FAILED,
            artifact_key=release.artifact_key,
            file_name=release.file_name,
            archive_size=release.archive_size,
            error_message=error_message,
            created_at=PassedDatetime(unwrap_value(release.created_at), now),
            started_at=release.started_at,
            finished_at=now,
        )
