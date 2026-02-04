from collections.abc import Mapping
from typing import Final

from domain.enums.project_roles import ProjectRole

SUBORDINATE_ROLES: Final[Mapping[ProjectRole, set[ProjectRole]]] = {
    ProjectRole.OWNER: {ProjectRole.LEAD, ProjectRole.MEMBER},
    ProjectRole.LEAD: {ProjectRole.MEMBER},
    ProjectRole.MEMBER: set(),
}
