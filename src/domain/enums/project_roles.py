__all__ = ["ProjectRole"]

from enum import StrEnum


class ProjectRole(StrEnum):
    OWNER = "OWNER"
    LEAD = "LEAD"
    MEMBER = "MEMBER"
