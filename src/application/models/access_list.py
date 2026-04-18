from typing import Sequence
from dataclasses import dataclass

from domain.value_objects import Name
from domain.entities.user import UserId
from domain.entities.project_group import ProjectGroupId
from domain.entities.access_list import AccessList


@dataclass(frozen=True)
class ProjectAccessListsRead:

    access_lists: Sequence[AccessList]
    owners: Sequence[Name | None]
    user_targets: dict[UserId, Name]
    group_targets: dict[ProjectGroupId, Name]