from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, UUID4

from domain.enums import ProjectUnitAction, ProjectRole


class AccessRule(BaseModel):
    action: ProjectUnitAction
    type: Literal["ALLOW", "DENY"]


class AccessRuleTargetUserPayload(BaseModel):
    kind: Literal["user"] = "user"
    user_id: UUID4


class AccessRuleTargetRolePayload(BaseModel):
    kind: Literal["role"] = "role"
    role: ProjectRole


class AccessRuleTargetGroupPayload(BaseModel):
    kind: Literal["group"] = "group"
    group_id: UUID4


AccessRuleTargetPayload = Annotated[
    Union[
        AccessRuleTargetUserPayload,
        AccessRuleTargetRolePayload,
        AccessRuleTargetGroupPayload,
    ],
    Field(discriminator="kind"),
]


class AccessRuleCreate(AccessRule):
    target: AccessRuleTargetPayload


class UserAccessRule(AccessRule):
    target: UUID4
    display_name: str


class RoleAccessRule(AccessRule):
    target: ProjectRole


class GroupAccessRule(AccessRule):
    target: UUID4
    display_name: str


class AccessListCreate(BaseModel):
    name: str
    rules: list[AccessRuleCreate]


class AccessListAssign(BaseModel):
    access_list_id: UUID4 | None


class AccessListCreated(BaseModel):
    id_: UUID4
    created_by: UUID4


class AccessListRead(AccessListCreated):
    name: str
    owner_name: str
    rules: list[UserAccessRule | RoleAccessRule | GroupAccessRule]
