from typing import Literal
from pydantic import BaseModel, UUID4

from domain.enums import ProjectUnitAction, ProjectRole


class AccessRule(BaseModel):

    action: ProjectUnitAction
    type: Literal["ALLOW", "DENY"]


class AccessRuleCreate(AccessRule):
    target: UUID4 | ProjectRole


class UserAccessRule(AccessRule):
    target: UUID4
    display_name: str


class RoleAccessRule(AccessRule):
    target: ProjectRole


class AccessListCreate(BaseModel):

    name: str
    rules: list[AccessRuleCreate]


class AccessListCreated(BaseModel):
    id_: UUID4
    created_by: UUID4


class AccessListRead(AccessListCreated):
    name: str
    owner_name: str
    rules: list[UserAccessRule | RoleAccessRule]
