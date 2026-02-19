from pydantic import BaseModel


class ContentTicketCreated(BaseModel):
    ticket: str
