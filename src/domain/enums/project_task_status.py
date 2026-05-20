from enum import StrEnum


class ProjectTaskStatus(StrEnum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    OVERDUE = "OVERDUE"
    CANCELED = "CANCELED"
