from dataclasses import dataclass

from domain.entities import ProjectTask, UserId
from domain.entities.project_group import ProjectGroupId
from domain.enums import ProjectRole
from domain.value_objects import Name


@dataclass(frozen=True)
class ProjectTaskGroupAssigneeRead:
    name: Name
    color: str


@dataclass(frozen=True)
class ProjectTaskDetailsRead:
    task: ProjectTask
    role_assignees: set[ProjectRole]
    user_assignees: dict[UserId, Name]
    group_assignees: dict[ProjectGroupId, ProjectTaskGroupAssigneeRead]
