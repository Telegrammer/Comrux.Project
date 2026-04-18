from datetime import datetime

from pydantic import BaseModel


class ProjectReleaseCreate(BaseModel):
    name: str


class ProjectReleaseCreatedResponse(BaseModel):
    release_id: str
    project_id: str
    status: str
    name: str


class ProjectReleaseReadResponse(BaseModel):
    id_: str
    project_id: str
    name: str
    status: str
    file_name: str | None
    archive_size: int | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class ProjectReleasesListResponse(BaseModel):
    items: list[ProjectReleaseReadResponse]
    total: int
