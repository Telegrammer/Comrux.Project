from datetime import datetime
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TaskListParams:
    batch_size: int
    current_resend_time: datetime
