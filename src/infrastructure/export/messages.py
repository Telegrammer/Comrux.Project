from pydantic import BaseModel


class ProjectReleaseCreatedMessage(BaseModel):
    project_id: str
    release_id: str

    model_config = {"extra": "ignore"}
