from dataclasses import dataclass

from domain.entities import Project, ProjectGroup, ProjectGroupId, ProjectId, User

from application.exceptions import ProjectGroupNotInProjectError
from application.ports.gateways import ProjectGroupQueryGateway, ProjectQueryGateway
from .current_user import CurrentUserService


@dataclass
class ProjectGroupManageContext:
    current_user: User
    pinned_project: Project
    found_group: ProjectGroup


class ProjectGroupManageContextService:
    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        group_queries: ProjectGroupQueryGateway,
    ) -> None:
        self._current_user = current_user
        self._project_queries = project_queries
        self._group_queries = group_queries

    async def __call__(
        self, project_id: ProjectId, group_id: ProjectGroupId
    ) -> ProjectGroupManageContext:
        current_user: User = await self._current_user()
        project: Project = await self._project_queries.by_id(project_id.value)
        group: ProjectGroup = await self._group_queries.by_id(group_id.value)

        if group.project_id != project.id_:
            raise ProjectGroupNotInProjectError("Given group is not in given project")

        return ProjectGroupManageContext(
            current_user=current_user,
            pinned_project=project,
            found_group=group,
        )
