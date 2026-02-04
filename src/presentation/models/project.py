__all__ = ["ProjectCreate", "ProjectCreated"]

from datetime import datetime
from pydantic import BaseModel


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


class ProjectUpdate(ProjectCreate): ...
