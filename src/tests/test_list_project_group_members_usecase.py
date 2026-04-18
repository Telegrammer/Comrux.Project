import asyncio
from types import SimpleNamespace

from application.services import ProjectGroupManageContext
from application.usecases import (
    ListProjectGroupMembersRequest,
    ListProjectGroupMembersUsecase,
)
from application.ports.gateways.query_params import OffsetPagination
from application.ports import UserListParams
from domain.entities import ProjectGroup, ProjectGroupId, ProjectId, UserId
from domain.enums import ProjectRole
from domain.value_objects import HexColor, Title


class ContextServiceStub:
    def __init__(self, context: ProjectGroupManageContext) -> None:
        self._context = context

    async def __call__(self, *_args, **_kwargs) -> ProjectGroupManageContext:
        return self._context


class UserQueriesStub:
    def __init__(self, users: list[object]) -> None:
        self._users = users

    async def by_ids(self, _ids, _params):
        return self._users


def test_list_project_group_members_returns_members() -> None:
    async def scenario() -> None:
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440060")
        participant_id = UserId("550e8400-e29b-41d4-a716-446655440061")
        project_id = ProjectId("550e8400-e29b-41d4-a716-446655440063")
        group_id = ProjectGroupId("550e8400-e29b-41d4-a716-446655440062")

        context = ProjectGroupManageContext(
            current_user=SimpleNamespace(id_=current_user_id.value),
            pinned_project=SimpleNamespace(
                members={
                    current_user_id: ProjectRole.OWNER,
                    participant_id: ProjectRole.MEMBER,
                }
            ),
            found_group=ProjectGroup(
                id_=group_id,
                project_id=project_id,
                name=Title("Team"),
                color=HexColor("#112233"),
                owner=current_user_id,
                participants=[participant_id],
                is_public=True,
            ),
        )
        user = SimpleNamespace(
            id_=participant_id.value,
            name="Teammate",
            bio="Member",
        )
        usecase = ListProjectGroupMembersUsecase(
            context_service=ContextServiceStub(context),
            user_queries=UserQueriesStub([user]),
        )

        response = await usecase(
            ListProjectGroupMembersRequest.from_primitives(
                project_id=project_id.value,
                group_id=group_id.value,
            ),
            UserListParams(
                filters=[],
                pagination=OffsetPagination(0, 10),
                sorting=[],
            ),
        )

        assert len(response) == 1
        assert response[0]["user_id"] == participant_id.value
        assert response[0]["role"] == ProjectRole.MEMBER

    asyncio.run(scenario())
