from functools import singledispatchmethod

from application.ports.mappers.errors import MappingError
from domain.entities import (
    ProjectGroupId,
    ProjectTaskAssignee,
    ProjectTaskGroupAssignee,
    ProjectTaskRoleAssignee,
    ProjectTaskUserAssignee,
)
from presentation.models import (
    ProjectTaskAssigneeGroupPayload,
    ProjectTaskAssigneeRolePayload,
    ProjectTaskAssigneeUserPayload,
)


class ProjectTaskAssigneePresenter:
    @singledispatchmethod
    def to_domain_assignee(self, target: object) -> ProjectTaskAssignee:
        raise MappingError(f"Unknown task assignee payload: {type(target)!r}")

    @to_domain_assignee.register
    def _(self, target: ProjectTaskAssigneeUserPayload) -> ProjectTaskAssignee:
        return ProjectTaskUserAssignee(str(target.user_id))

    @to_domain_assignee.register
    def _(self, target: ProjectTaskAssigneeRolePayload) -> ProjectTaskAssignee:
        return ProjectTaskRoleAssignee(target.role)

    @to_domain_assignee.register
    def _(self, target: ProjectTaskAssigneeGroupPayload) -> ProjectTaskAssignee:
        return ProjectTaskGroupAssignee(ProjectGroupId(str(target.group_id)))
