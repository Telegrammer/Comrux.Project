from pydantic import BaseModel, UUID4


class ProjectGroupCreate(BaseModel):
    name: str
    color: str
    is_public: bool = False
    participants: list[UUID4] = []


class ProjectGroupCreated(BaseModel):
    group_id: UUID4
    owner_id: UUID4
    project_id: UUID4


class ProjectGroupRead(BaseModel):
    id_: UUID4
    name: str
    color: str
    owner: UUID4
    is_public: bool
    participants_count: int


class ProjectGroupJoin(BaseModel):
    participant_id: UUID4
