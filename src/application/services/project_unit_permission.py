from domain.entities import User, Project, UserId
from domain.entities.project_unit import ProjectUnitId
from domain.entities.access_list import ResolvedUnitPermissions
from domain.services import AccessListService
from application.ports.gateways import AccessListQueryGateway, ProjectGroupQueryGateway
from application.ports.authorization import (
    authorize,
    CanManageProjectContent,
    ProjectContentManagmentContext,
)


class ProjectUnitPermissionService:
    def __init__(
        self,
        acl_queries: AccessListQueryGateway,
        acl_service: AccessListService,
        group_queries: ProjectGroupQueryGateway,
    ):
        self._acl_queries = acl_queries
        self._acl_service = acl_service
        self._group_queries = group_queries

    async def __call__(
        self, current_user: User, pinned_project: Project, unit_id: ProjectUnitId
    ) -> ResolvedUnitPermissions:

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=current_user, target=pinned_project
            ),
        )

        acl_subtree = await self._acl_queries.by_project_unit(unit_id.value)
        user_group_ids = await self._group_queries.group_ids_for_user(
            pinned_project.id_,
            current_user.id_,
        )
        return self._acl_service.resolve_permissions(
            project=pinned_project,
            access_lists=acl_subtree,
            user_id=UserId(current_user.id_),
            user_project_group_ids=user_group_ids,
        )
