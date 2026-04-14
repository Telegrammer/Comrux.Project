from __future__ import annotations

import base64
from collections import defaultdict
from typing import Sequence

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.export import (
    GroupPublishedContentGateway,
    ProjectReleaseCommandGateway,
    ProjectReleaseQueryGateway,
    ProjectTreeNodeSnapshot,
    ProjectTreeSnapshotGateway,
    PublishedGroupContent,
)
from application.ports.gateways.errors import GatewayFailedError
from domain.entities.project import ProjectId
from domain.entities.user import UserId
from domain.export import ProjectRelease, ProjectReleaseId, ProjectReleaseStatus
from domain.value_objects import PassedDatetime
from infrastructure.export.models import ProjectReleaseOrm
from infrastructure.models.project_unit_node import ProjectUnitNode
from setup.config import Settings


def _to_domain_release(dto: ProjectReleaseOrm) -> ProjectRelease:
    return ProjectRelease(
        id_=ProjectReleaseId(str(dto.id_)),
        project_id=ProjectId(str(dto.project_id)),
        requested_by=UserId(str(dto.requested_by)),
        name=dto.name,
        status=dto.status,
        artifact_key=dto.artifact_key,
        file_name=dto.file_name,
        archive_size=dto.archive_size,
        error_message=dto.error_message,
        created_at=PassedDatetime(dto.created_at, dto.created_at),
        started_at=dto.started_at,
        finished_at=dto.finished_at,
    )


def _to_dto_release(entity: ProjectRelease) -> ProjectReleaseOrm:
    return ProjectReleaseOrm(
        id_=entity.id_,
        project_id=entity.project_id,
        requested_by=entity.requested_by,
        name=entity.name,
        status=entity.status,
        artifact_key=entity.artifact_key,
        file_name=entity.file_name,
        archive_size=entity.archive_size,
        error_message=entity.error_message,
        created_at=entity.created_at,
        started_at=entity.started_at,
        finished_at=entity.finished_at,
    )


class SqlAlchemyProjectReleaseCommandGateway(ProjectReleaseCommandGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, release: ProjectRelease) -> None:
        self._session.add(_to_dto_release(release))
        await self._session.flush()

    async def update(self, release: ProjectRelease) -> None:
        await self._session.merge(_to_dto_release(release))
        await self._session.flush()


class SqlAlchemyProjectReleaseQueryGateway(ProjectReleaseQueryGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def by_id(self, release_id: ProjectReleaseId) -> ProjectRelease | None:
        dto = await self._session.get(ProjectReleaseOrm, release_id)
        if dto is None:
            return None
        return _to_domain_release(dto)


class SqlAlchemyProjectTreeSnapshotGateway(ProjectTreeSnapshotGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def by_project(self, project_id: ProjectId) -> Sequence[ProjectTreeNodeSnapshot]:
        stmt = (
            select(ProjectUnitNode)
            .where(ProjectUnitNode.project_id == project_id)
            .order_by(ProjectUnitNode.parent_id, ProjectUnitNode.name)
        )
        nodes = (await self._session.execute(stmt)).scalars().all()
        nodes_by_id = {str(node.id_): node for node in nodes}
        children_by_parent: dict[str | None, list[ProjectUnitNode]] = defaultdict(list)
        for node in nodes:
            parent_key = str(node.parent_id) if node.parent_id is not None else None
            children_by_parent[parent_key].append(node)

        snapshots: list[ProjectTreeNodeSnapshot] = []
        root_nodes = [node for node in nodes if node.parent_id is None]
        stack: list[tuple[ProjectUnitNode, str]] = [
            (node, "") for node in reversed(root_nodes)
        ]

        while stack:
            node, parent_path = stack.pop()
            current_path = (
                node.name
                if parent_path == "" or node.name == ""
                else f"{parent_path}/{node.name}"
            )
            if node.parent_id is not None:
                snapshots.append(
                    ProjectTreeNodeSnapshot(
                        path=current_path,
                        unit_type=node.unit_type.value,
                        content_ref=node.attributes.get("content_ref"),
                    )
                )
            for child in reversed(children_by_parent.get(str(node.id_), [])):
                stack.append((child, current_path))
        return snapshots


class HttpGroupPublishedContentGateway(GroupPublishedContentGateway):
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.collaboration.base_url.rstrip("/")
        self._group_content_path = settings.collaboration.group_content_path
        self._timeout_seconds = settings.collaboration.timeout_seconds

    async def by_group(self, group_id: ProjectId) -> Sequence[PublishedGroupContent]:
        path = self._group_content_path.format(group_id=group_id.value)
        url = f"{self._base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(url)
                response.raise_for_status()
        except (httpx.HTTPError, ValueError) as error:
            raise GatewayFailedError(
                "Cannot list group content: collaboration service is unavailable"
            ) from error

        payload = response.json()
        return [
            PublishedGroupContent(
                content_id=item["content_id"],
                content=base64.b64decode(item["content"]),
            )
            for item in payload
        ]
