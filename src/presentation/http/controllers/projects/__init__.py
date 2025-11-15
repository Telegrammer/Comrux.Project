from fastapi import APIRouter
from .create_project import create_create_project_router
from .list_projects import create_list_projects_router


projects_router = APIRouter(prefix="/project", tags=["project"])
projects_router.include_router(create_create_project_router())
projects_router.include_router(create_list_projects_router())
