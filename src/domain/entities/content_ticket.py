from dataclasses import dataclass, field

from datetime import datetime
from .base import Entity
from .user import UserId
from .document import ContentId
from ..value_objects import Uuid4, Name, PassedDatetime, FutureDatetime
from ..exceptions import DomainFieldError
from ..enums import ProjectUnitAction


class ContentTicketId(Uuid4): ...


@dataclass
class ContentTicket(Entity[ContentTicketId]):
    username: Name
    user_id: UserId
    content_ref: ContentId
    permissions: list[ProjectUnitAction] = field(default_factory=[])
    issued_at: PassedDatetime
    expire_at: FutureDatetime


    def __post_init__(self):

        if self.issued_at >= self.expire_at:
            raise DomainFieldError("Content ticket have impossible/pointless lifetime")