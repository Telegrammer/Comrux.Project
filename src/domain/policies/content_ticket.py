from datetime import timedelta
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContentTicketValidityPolicy:
    ttl: timedelta
