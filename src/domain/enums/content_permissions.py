from enum import StrEnum


class ProjectUnitAction(StrEnum):

    READ = "r"
    WRITE = "w"
    EXECUTE = "x"
    SECURE = "s"
