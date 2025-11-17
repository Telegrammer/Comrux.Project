from fastapi import APIRouter
from .create_project import create_create_project_router
from .list_projects import create_list_projects_router
from .update_project import create_update_project_router
from .delete_project import create_delete_project_router


projects_router = APIRouter(prefix="/project", tags=["project"])
projects_router.include_router(create_create_project_router())
projects_router.include_router(create_list_projects_router())
projects_router.include_router(create_update_project_router())
projects_router.include_router(create_delete_project_router())
