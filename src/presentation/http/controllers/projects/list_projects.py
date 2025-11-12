__all__ = ["create_list_projects_router"]


from fastapi_error_map import ErrorAwareRouter


def create_list_projects_router():

    router = ErrorAwareRouter()

    @router.get("/list")
    async def list_projects():
        return {"name": "project1"}

    return  router