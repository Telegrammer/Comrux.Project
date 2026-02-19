from enum import StrEnum


class TaskStatus(StrEnum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
