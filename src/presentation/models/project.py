from datetime import datetime
from pydantic import BaseModel, UUID4
from domain.enums import ProjectRole


class ProjectCreate(BaseModel):
    title: str
    description: str


class ProjectCreated(BaseModel):
    project_id: str


class ProjectRead(ProjectCreate):
    id_: str
    owner_id: str
    members_count: int
    created_at: datetime


class CurrentUserProjectRead(ProjectCreate):
    id_: str
    role: ProjectRole | None
    created_at: datetime


class ProjectUpdate(ProjectCreate): ...


class ProjectMemberAdd(BaseModel):

    user: UUID4


class ProjectMemberAdded(BaseModel):
    member: str
    project: str


class ProjectMemberRead(BaseModel):
    user_id: UUID4
    name: str
    bio: str
    role: ProjectRole


class ProjectMemberRemoved(BaseModel):
    member: str
    project: str


class ProjectMemberRemove(BaseModel):
    user: UUID4


class ProjectGrantOwner(BaseModel):
    user: UUID4


class ProjectOwnerGranted(BaseModel):
    old_owner: str
    new_role: str
    project: str
