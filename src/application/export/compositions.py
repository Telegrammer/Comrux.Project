from __future__ import annotations

import asyncio
import logging

from application.ports.gateways.errors import GatewayFailedError
from application.export.contracts import (
    GroupPublishedContentGateway,
    ProjectReleaseArtifactGateway,
    ProjectReleaseCommandGateway,
    ProjectReleaseQueryGateway,
    ProjectTreeSnapshotGateway,
)
from application.export.usecases import CreateProjectReleaseRequest, CreateProjectReleaseUsecase
from application.ports import Clock, TaskCommandGateway, UnitOfWork
from domain.entities import Task
from domain.entities.project import ProjectId
from domain.export import ProjectRelease, ProjectReleaseId, ProjectReleaseService, ProjectReleaseStatus
from domain.services import TaskService
from utils import unwrap_value

logger = logging.getLogger(__name__)


class CreateProjectReleaseComposition:
    _task_type = "project.releases.created"

    def __init__(
        self,
        clock: Clock,
        unit_of_work: UnitOfWork,
        usecase: CreateProjectReleaseUsecase,
        release_commands: ProjectReleaseCommandGateway,
        task_service: TaskService,
        task_gateway: TaskCommandGateway,
    ) -> None:
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._usecase = usecase
        self._release_commands = release_commands
        self._task_service = task_service
        self._task_gateway = task_gateway

    async def __call__(
        self,
        request: CreateProjectReleaseRequest,
    ) -> ProjectRelease:
        async with self._unit_of_work:
            release = await self._usecase(request)
            await self._release_commands.add(release)
            task: Task = self._task_service.create_task(
                self._task_type,
                {
                    "project_id": unwrap_value(release.project_id),
                    "release_id": unwrap_value(release.id_),
                },
                now=self._clock.now(),
            )
            await self._task_gateway.add(task)
        return release


class BuildProjectReleaseComposition:
    def __init__(
        self,
        clock: Clock,
        unit_of_work: UnitOfWork,
        release_queries: ProjectReleaseQueryGateway,
        release_commands: ProjectReleaseCommandGateway,
        release_service: ProjectReleaseService,
        tree_snapshots: ProjectTreeSnapshotGateway,
        group_content: GroupPublishedContentGateway,
        artifacts: ProjectReleaseArtifactGateway,
    ) -> None:
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._release_queries = release_queries
        self._release_commands = release_commands
        self._release_service = release_service
        self._tree_snapshots = tree_snapshots
        self._group_content = group_content
        self._artifacts = artifacts

    @staticmethod
    def _to_failure_message(error: Exception) -> str:
        if isinstance(error, FileNotFoundError):
            return str(error)
        if isinstance(error, GatewayFailedError):
            return str(error)
        return "Unexpected error while building project release"

    async def __call__(self, project_id: str, release_id: str) -> None:
        release = await self._release_queries.by_id(ProjectReleaseId(release_id))
        if release is None:
            logger.warning("Release %s was not found", release_id)
            return
        if unwrap_value(release.project_id) != project_id:
            logger.warning(
                "Release %s does not belong to project %s",
                release_id,
                project_id,
            )
            return
        if release.status is not ProjectReleaseStatus.CREATED:
            logger.info("Release %s is already in status %s", release_id, release.status)
            return

        now = self._clock.now()
        processing_release = self._release_service.mark_processing(release, now)
        async with self._unit_of_work:
            await self._release_commands.update(processing_release)

        try:
            release_project_id = ProjectId(str(unwrap_value(processing_release.project_id)))
            tree_snapshot, group_contents = await asyncio.gather(
                self._tree_snapshots.by_project(release_project_id),
                self._group_content.by_group(release_project_id),
            )
            artifact = await self._artifacts.build_and_store(
                release=processing_release,
                tree=tree_snapshot,
                contents=group_contents,
                finished_at=self._clock.now(),
            )
            ready_release = self._release_service.mark_ready(
                processing_release,
                artifact_key=artifact.artifact_key,
                file_name=artifact.file_name,
                archive_size=artifact.archive_size,
                now=self._clock.now(),
            )
            async with self._unit_of_work:
                await self._release_commands.update(ready_release)
        except Exception as error:
            failed_release = self._release_service.mark_failed(
                processing_release,
                error_message=self._to_failure_message(error),
                now=self._clock.now(),
            )
            async with self._unit_of_work:
                await self._release_commands.update(failed_release)
            logger.exception("Project release %s failed", release_id)
