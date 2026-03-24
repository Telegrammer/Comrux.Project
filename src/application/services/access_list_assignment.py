from __future__ import annotations
from domain import AccessListId, Project, ProjectUnit, User, ProjectUnitId
from domain.enums import ProjectUnitAction

from application.exceptions import AccessListNotInProjectError
from application.exceptions.authorization import AccessDeniedError
from application.ports.authorization import (
    authorize,
    CanAssignAccessList,
    ProjectContentManagmentContext,
)
from application.ports.gateways import (
    AccessListQueryGateway,
    ProjectUnitCommandGateway,
)

from .project_unit_permission import ProjectUnitPermissionService


class AssignAccessListService:
    def __init__(
        self,
        acl_queries: AccessListQueryGateway,
        unit_permissions: ProjectUnitPermissionService,
        unit_commands: ProjectUnitCommandGateway,
    ) -> None:
        self._acl_queries = acl_queries
        self._unit_permissions = unit_permissions
        self._unit_commands = unit_commands

    async def __call__(
        self,
        current_user: User,
        project: Project,
        unit: ProjectUnit,
        access_list_id: AccessListId | None,
    ) -> None:
        permissions = await self._unit_permissions(
            current_user, project, ProjectUnitId(unit.id_)
        )

        if ProjectUnitAction.SECURE in permissions.denied:
            raise AccessDeniedError("Access list assignment is explicitly denied")

        if ProjectUnitAction.SECURE not in permissions.allowed:
            authorize(
                CanAssignAccessList(),
                context=ProjectContentManagmentContext(
                    subject=current_user, target=project
                ),
            )

        if access_list_id is None:
            unit.access_list = None
            await self._unit_commands.update(unit)
            return

        access_list = await self._acl_queries.by_id(access_list_id.value)
        if access_list.project != project.id_:
            raise AccessListNotInProjectError(
                "Given access list doesen't belongs to the project"
            )

        unit.access_list = access_list.id_
        await self._unit_commands.update(unit)
