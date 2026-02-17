from pydantic import BaseModel, UUID4


class NameCursor(BaseModel):
    name: str
    latest_id: str
