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
    created_at: datetime
