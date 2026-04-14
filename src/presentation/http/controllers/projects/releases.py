from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from pydantic import UUID4
from starlette import status
from starlette.responses import Response

from application.exceptions import (
    AccessDeniedError,
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
    ProjectReleaseNotFoundError,
    ProjectReleaseNotReadyError,
)
from application.ports.gateways.errors import GatewayFailedError
from presentation.export import (
    ProjectReleaseCreate,
    CreateProjectReleaseHandler,
    DownloadProjectReleaseHandler,
    GetProjectReleaseHandler,
    ProjectReleaseCreatedResponse,
    ProjectReleaseReadResponse,
)
from presentation.http.controllers.dependencies import (
    http_bearer,
    log_info,
    service_unavailable_rule,
)


def create_project_release_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/{project_id}/releases",
        error_map={
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        response_model=ProjectReleaseCreatedResponse,
    )
    @inject
    async def create_release(
        project_id: Annotated[UUID4, Path()],
        request_body: ProjectReleaseCreate,
        handler: FromDishka[CreateProjectReleaseHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ) -> ProjectReleaseCreatedResponse:
        del token
        return await handler(project_id, request_body)

    @router.get(
        "/{project_id}/releases/{release_id}",
        error_map={
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectReleaseNotFoundError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_model=ProjectReleaseReadResponse,
    )
    @inject
    async def get_release(
        project_id: Annotated[UUID4, Path()],
        release_id: Annotated[UUID4, Path()],
        handler: FromDishka[GetProjectReleaseHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ) -> ProjectReleaseReadResponse:
        del token
        return await handler(project_id, release_id)

    @router.get(
        "/{project_id}/releases/{release_id}/download",
        error_map={
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectReleaseNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectReleaseNotReadyError: status.HTTP_409_CONFLICT,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_class=Response,
        responses={200: {"content": {"application/zip": {}}}},
    )
    @inject
    async def download_release(
        project_id: Annotated[UUID4, Path()],
        release_id: Annotated[UUID4, Path()],
        handler: FromDishka[DownloadProjectReleaseHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ) -> Response:
        del token
        artifact = await handler(project_id, release_id)
        return Response(
            content=artifact.content,
            media_type=artifact.media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{artifact.file_name}"'
            },
        )

    return router
