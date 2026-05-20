__all__ = ["TimestampClock"]

from application.ports import Clock
from datetime import datetime, UTC


class TimestampClock(Clock):
    def now(self) -> datetime:
        return datetime.now(tz=None)

    def normalize(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt
        return dt.astimezone(UTC).replace(tzinfo=None)
