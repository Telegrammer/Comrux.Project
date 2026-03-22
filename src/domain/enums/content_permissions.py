from enum import StrEnum


class ProjectUnitAction(StrEnum):

    READ = "r"
    WRITE = "w"
    EXECUTE = "x"


class ContentPermission(StrEnum):

    VIEW = "view"
    EDIT = "edit"
