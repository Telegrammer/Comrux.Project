from fastapi import APIRouter
from .list_projects import create_list_projects_router

current_user_router = APIRouter(prefix="/me")
current_user_router.include_router(create_list_projects_router())
