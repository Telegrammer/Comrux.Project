from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .base import AggregationRoot
from .project import ProjectId
from .user import UserId
from ..enums import ProjectTaskStatus
from ..exceptions import DomainFieldError
from ..value_objects import Uuid4
from .responsible import (
    Responsible as ProjectTaskAssignee,
    ResponsibleVisitor as ProjectTaskAssigneeVisitor,
    UserResponsible as ProjectTaskUserAssignee,
    RoleResponsible as ProjectTaskRoleAssignee,
    GroupResponsible as ProjectTaskGroupAssignee,
)


class ProjectTaskId(Uuid4): ...


@dataclass(kw_only=True)
class ProjectTask(AggregationRoot[ProjectTaskId]):
    project_id: ProjectId
    title: str
    description: str
    status: ProjectTaskStatus
    creator_id: UserId
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime
    assignees: list[ProjectTaskAssignee] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise DomainFieldError("Task title cannot be empty")
        if self.end_at <= self.start_at:
            raise DomainFieldError("Task end_at must be greater than start_at")
