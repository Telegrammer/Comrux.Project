from fastapi import APIRouter
from .list_projects import create_list_projects_router


projects_router = APIRouter(prefix="/project", tags=["project"])
projects_router.include_router(create_list_projects_router())
