from datetime import datetime, timedelta
from domain.value_objects import Name, PassedDatetime, FutureDatetime
from domain.entities import User, ContentTicket, UserId
from domain.entities.document import ContentId
from domain.enums import ContentPermission
from domain.ports.id_generators import ContentIdGenerator
from domain.policies import ContentTicketValidityPolicy


class ContentTicketService:

    def __init__(
        self,
        id_generator: ContentIdGenerator,
        validaty_policy: ContentTicketValidityPolicy,
    ):
        self._id_generator: ContentIdGenerator = id_generator
        self._validaty_policy: ContentTicketValidityPolicy = validaty_policy

    def create_ticket(
        self,
        user: User,
        now: datetime,
        permissions: list[ContentPermission],
        content_ref: ContentId,
    ) -> ContentTicket:
        return ContentTicket(
            id_=self._id_generator(),
            username=Name(user.name),
            user_id=UserId(user.id_),
            content_ref=ContentId(content_ref),
            permissions=permissions,
            issued_at=PassedDatetime(now, now),
            expire_at=FutureDatetime(now + self._validaty_policy.ttl, now),
        )
