from fastapi import APIRouter
from .create_project import create_create_project_router
from .list_projects import create_list_projects_router
from .update_project import create_update_project_router
from .delete_project import create_delete_project_router
from .grant_owner import create_grant_owner_router
from .add_member import create_add_member_router
from .remove_member import create_remove_member_router
from .list_members import create_list_members_router
from .set_role import create_set_role_router

projects_router = APIRouter(prefix="/project", tags=["project"])
projects_router.include_router(create_create_project_router())
projects_router.include_router(create_list_projects_router())
projects_router.include_router(create_update_project_router())
projects_router.include_router(create_delete_project_router())
projects_router.include_router(create_grant_owner_router())
projects_router.include_router(create_add_member_router())
projects_router.include_router(create_list_members_router())
projects_router.include_router(create_remove_member_router())
projects_router.include_router(create_set_role_router())
