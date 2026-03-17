from fastapi import APIRouter
from .list_projects import create_list_projects_router
from .get_profile import create_get_profile_router

# Mounted under `/user` in `users_router`, so paths here are absolute after `/user`.
# We expose:
#   - GET /user/me           (current user profile)
#   - GET /user/me/projects  (current user's projects)
current_user_router = APIRouter(prefix="")
current_user_router.include_router(create_get_profile_router())
current_user_router.include_router(create_list_projects_router())
