import asyncio
from types import SimpleNamespace

import pytest

from application.exceptions import AccessDeniedError
from application.services import ProjectGroupManageContext
from application.usecases import (
    DeleteProjectGroupRequest,
    DeleteProjectGroupUsecase,
)
from domain.entities import ProjectGroup, ProjectGroupId, ProjectId, UserId
from domain.enums import ProjectRole
from domain.value_objects import HexColor, Title


class ContextServiceStub:
    def __init__(self, context: ProjectGroupManageContext) -> None:
        self._context = context

    async def __call__(self, *_args, **_kwargs) -> ProjectGroupManageContext:
        return self._context


class GroupCommandsStub:
    def __init__(self) -> None:
        self.deleted = False

    async def delete(self, _group: ProjectGroup) -> None:
        self.deleted = True


def test_delete_group_denies_non_owner_non_project_owner() -> None:
    async def scenario() -> None:
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440030")
        group_owner_id = UserId("550e8400-e29b-41d4-a716-446655440031")
        group = ProjectGroup(
            id_=ProjectGroupId("550e8400-e29b-41d4-a716-446655440032"),
            project_id=ProjectId("550e8400-e29b-41d4-a716-446655440033"),
            name=Title("Ops"),
            color=HexColor("#112233"),
            owner=group_owner_id,
            participants=[],
            is_public=False,
        )
        context = ProjectGroupManageContext(
            current_user=SimpleNamespace(id_=current_user_id.value),
            pinned_project=SimpleNamespace(
                members={current_user_id: ProjectRole.MEMBER},
            ),
            found_group=group,
        )
        commands = GroupCommandsStub()
        usecase = DeleteProjectGroupUsecase(
            context_service=ContextServiceStub(context),
            group_commands=commands,
        )

        with pytest.raises(AccessDeniedError):
            await usecase(
                DeleteProjectGroupRequest.from_primitives(
                    project_id=str(group.project_id),
                    group_id=str(group.id_),
                )
            )
        assert commands.deleted is False

    asyncio.run(scenario())
