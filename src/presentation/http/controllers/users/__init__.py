from fastapi import APIRouter
from .create_user import create_create_user_router
from .current_user import current_user_router
users_router = APIRouter(prefix="/user", tags=["user"])
users_router.include_router(create_create_user_router())
users_router.include_router(current_user_router)
