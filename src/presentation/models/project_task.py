from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, UUID4
from domain.enums import ProjectRole


class ProjectTaskAssigneeUserPayload(BaseModel):
    kind: Literal["user"] = "user"
    user_id: UUID4


class ProjectTaskAssigneeRolePayload(BaseModel):
    kind: Literal["role"] = "role"
    role: ProjectRole


class ProjectTaskAssigneeGroupPayload(BaseModel):
    kind: Literal["group"] = "group"
    group_id: UUID4


ProjectTaskAssigneePayload = Annotated[
    Union[
        ProjectTaskAssigneeUserPayload,
        ProjectTaskAssigneeRolePayload,
        ProjectTaskAssigneeGroupPayload,
    ],
    Field(discriminator="kind"),
]


class ProjectTaskCreate(BaseModel):
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    assignees: list[ProjectTaskAssigneePayload] = []


class ProjectTaskCreateUser(BaseModel):
    assignee_kind: Literal["user"] = "user"
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    assignees: list[ProjectTaskAssigneeUserPayload] = []


class ProjectTaskCreateRole(BaseModel):
    assignee_kind: Literal["role"] = "role"
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    assignees: list[ProjectTaskAssigneeRolePayload] = []


class ProjectTaskCreateGroup(BaseModel):
    assignee_kind: Literal["group"] = "group"
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    assignees: list[ProjectTaskAssigneeGroupPayload] = []


ProjectTaskCreateByKind = Annotated[
    Union[
        ProjectTaskCreateUser,
        ProjectTaskCreateRole,
        ProjectTaskCreateGroup,
    ],
    Field(discriminator="assignee_kind"),
]


class ProjectTaskCreated(BaseModel):
    task_id: UUID4
    project_id: UUID4


class ProjectTaskRead(BaseModel):
    id_: UUID4
    title: str
    description: str
    status: str


class ProjectTaskAssigneeRead(BaseModel):
    kind: Literal["user", "group", "role"]
    id_: str
    name: str
    color: str | None = None


class ProjectTaskDetailsRead(BaseModel):
    id_: UUID4
    project_id: UUID4
    creator_id: UUID4
    creator_email: str | None
    creator_name: str
    title: str
    description: str
    status: str
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime
    assignees: list[ProjectTaskAssigneeRead]


class ProjectTaskSetStatus(BaseModel):
    status: Literal["complete", "cancel"]


class ProjectTaskStatusChanged(BaseModel):
    task_id: UUID4
    status: str
