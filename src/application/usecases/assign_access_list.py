from dataclasses import dataclass

from domain import (
    AccessListId,
    ProjectId,
    ProjectUnitId,
    DirectoryId,
    DocumentId,
)

from application.services import (
    AssignAccessListService,
    DirectoryManageContextService,
    DocumentManageContextService,
)


@dataclass
class AssignAccessListRequest:
    project_id: ProjectId
    unit_id: ProjectUnitId
    access_list_id: AccessListId | None

    @classmethod
    def from_primitives(
        cls, project_id: str, unit_id: str, access_list_id: str | None
    ) -> "AssignAccessListRequest":
        return cls(
            project_id=ProjectId(project_id),
            unit_id=ProjectUnitId(unit_id),
            access_list_id=(
                AccessListId(access_list_id) if access_list_id is not None else None
            ),
        )


class AssignAccessListToDirectoryUsecase:
    def __init__(
        self,
        context_service: DirectoryManageContextService,
        assign_access_list_service: AssignAccessListService,
    ) -> None:
        self._context_service = context_service
        self._assign_access_list_service = assign_access_list_service

    async def __call__(self, request: AssignAccessListRequest) -> None:
        context = await self._context_service(
            request.project_id, DirectoryId(request.unit_id.value)
        )
        await self._assign_access_list_service(
            current_user=context.current_user,
            project=context.pinned_project,
            unit=context.found_directory,
            access_list_id=request.access_list_id,
        )


class AssignAccessListToDocumentUsecase:
    def __init__(
        self,
        context_service: DocumentManageContextService,
        assign_access_list_service: AssignAccessListService,
    ) -> None:
        self._context_service = context_service
        self._assign_access_list_service = assign_access_list_service

    async def __call__(self, request: AssignAccessListRequest) -> None:
        context = await self._context_service(
            request.project_id, DocumentId(request.unit_id.value)
        )
        await self._assign_access_list_service(
            current_user=context.current_user,
            project=context.pinned_project,
            unit=context.found_document,
            access_list_id=request.access_list_id,
        )
