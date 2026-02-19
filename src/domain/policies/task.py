from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class TaskPolicy:
    init_resend_delta: timedelta
    backoff_value: float
    max_attempt_count: int
