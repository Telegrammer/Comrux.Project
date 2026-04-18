from .composite import AnyOf, AllOf
from .permissions import (
    CanDeleteProject,
    CanManageRole,
    CanManageSelf,
    CanManageProjectContent,
    CanUpdateProject,
    RoleManagementContext,
    UserManagementContext,
    ProjectManagmentContext,
    ProjectContentManagmentContext,
    ProjectGroupManagmentContext,
    CanDeleteAccessList,
    AccessListManagmentContext,
    CanAssignAccessList,
    CanChangePrivateness,
    CanManageProjectGroup,
    CanAddGroupParticipant,
    ProjectGroupParticipantManagmentContext,
)
from .authorize import authorize
