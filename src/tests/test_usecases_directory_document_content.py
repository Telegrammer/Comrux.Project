# Тесты усиливают protection и refactor-resistance для сценариев списка содержимого каталога,
# создания/удаления документов, создания каталога и выдачи content ticket.
# target_file: src/tests/test_usecases_directory_document_content.py — юзкейсы list/create/delete document/directory и create content ticket.

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
import jwt

from application.compositions import DeleteDirectoryComposition, DeleteDocumentComposition
from application.exceptions import (
    AccessDeniedError,
    DirectoryNotFoundError,
    DocumentNotFoundError,
    ProjectGroupNotInProjectError,
    UserNotInProjectGroupError,
)
from application.ports.gateways.query_params import ProjectUnitListParams
from application.ports.gateways.query_params.common import OffsetPagination
from application.usecases.create_content_ticket import (
    CreateContentTicketRequest,
    CreateContentTicketResponse,
    CreateContentTicketUsecase,
)
from presentation.presenters.auth_info.jwt_content_ticket_presenter import (
    JwtContentTicketPresenter,
)
from application.usecases.get_document_content import (
    GetDocumentContentRequest,
    GetDocumentContentUsecase,
)
from application.usecases.create_directory import (
    CreateDirectoryRequest,
    CreateDirectoryUsecase,
)
from application.usecases.create_document import CreateDocumentRequest, CreateDocumentUsecase
from application.usecases.delete_directory import (
    DeleteDirectoryRequest,
    DeleteDirectoryResponse,
    DeleteDirectoryUsecase,
)
from application.usecases.delete_document import (
    DeleteDocumentRequest,
    DeleteDocumentResponse,
    DeleteDocumentUsecase,
)
from application.usecases.list_directory_content import (
    ListDirectoryContentRequest,
    ListDirectoryContentUsecase,
)
from domain.entities import (
    DirectoryId,
    DocumentId,
    ProjectGroupId,
    ProjectId,
    UserId,
)
from domain.entities.access_list import ResolvedUnitPermissions
from domain.entities.document import ContentId
from domain.enums import ProjectUnitAction
from domain.value_objects import FileName, HexColor, Name, Title


def _project_unit_list_params() -> ProjectUnitListParams:
    return ProjectUnitListParams(
        filters=[],
        pagination=OffsetPagination(offset=0, limit=20),
        sorting=[],
    )


def test_list_directory_content_calls_visitor_when_execute_allowed() -> None:
    async def scenario() -> None:
        parent_uuid: str = "00000000-0000-4000-8000-000000000001"
        project_uuid: str = "00000000-0000-4000-8000-000000000002"
        directory_uuid: str = "00000000-0000-4000-8000-000000000003"
        owner_uuid: str = "00000000-0000-4000-8000-000000000004"

        # id/parent as str: use case wraps them in ProjectUnitId(...) (expects str, not VO)
        found_directory = SimpleNamespace(
            id_=directory_uuid,
            parent=parent_uuid,
        )
        found_project = SimpleNamespace(id_=project_uuid, is_private=True)

        directory_gateway = SimpleNamespace(
            by_id=AsyncMock(return_value=found_directory),
        )
        project_queries = SimpleNamespace(
            by_id=AsyncMock(return_value=found_project),
        )
        unit_stub = SimpleNamespace(created_by=UserId(owner_uuid))
        project_unit_gateway = SimpleNamespace(
            by_id=AsyncMock(),
            by_directory=AsyncMock(return_value=[unit_stub]),
        )
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.EXECUTE},
                denied=set(),
            )
        )
        owner_user = SimpleNamespace(id_=owner_uuid)
        user_gateway = SimpleNamespace(
            by_ids=AsyncMock(return_value=[owner_user]),
        )
        current_user = AsyncMock(return_value=SimpleNamespace(id_="u1"))

        directory_service = SimpleNamespace(belongs_to=MagicMock(return_value=True))
        use_case = ListDirectoryContentUsecase(
            directory_service=directory_service,
            directory_gateway=directory_gateway,
            project_unit_gateway=project_unit_gateway,
            project_queries=project_queries,
            permissions=permission_service,
            user_gateway=user_gateway,
            current_user=current_user,
        )
        visitor = MagicMock()
        request = ListDirectoryContentRequest(
            project_id=ProjectId(project_uuid),
            parent_id=DirectoryId(directory_uuid),
        )

        await use_case(visitor, request, _project_unit_list_params())

        visitor.visit_sequence.assert_called_once()
        call_args = visitor.visit_sequence.call_args
        assert call_args[0][0] == [unit_stub]
        owner_map = call_args[0][1]
        assert UserId(owner_uuid) in owner_map
        assert owner_map[UserId(owner_uuid)] is owner_user

    asyncio.run(scenario())


def test_list_directory_content_raises_when_execute_denied() -> None:
    async def scenario() -> None:
        parent_uuid: str = "00000000-0000-4000-8000-000000000011"
        project_uuid: str = "00000000-0000-4000-8000-000000000012"
        directory_uuid: str = "00000000-0000-4000-8000-000000000013"

        # id/parent as str: use case wraps them in ProjectUnitId(...) (expects str, not VO)
        found_directory = SimpleNamespace(
            id_=directory_uuid,
            parent=parent_uuid,
        )
        found_project = SimpleNamespace(id_=project_uuid, is_private=True)

        directory_gateway = SimpleNamespace(
            by_id=AsyncMock(return_value=found_directory),
        )
        project_queries = SimpleNamespace(
            by_id=AsyncMock(return_value=found_project),
        )
        project_unit_gateway = SimpleNamespace(
            by_directory=AsyncMock(),
        )
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed=set(),
                denied={ProjectUnitAction.EXECUTE},
            )
        )
        user_gateway = SimpleNamespace(
            by_ids=AsyncMock(),
        )
        current_user = AsyncMock(return_value=SimpleNamespace(id_="u1"))

        directory_service = SimpleNamespace(belongs_to=MagicMock(return_value=True))
        use_case = ListDirectoryContentUsecase(
            directory_service=directory_service,
            directory_gateway=directory_gateway,
            project_unit_gateway=project_unit_gateway,
            project_queries=project_queries,
            permissions=permission_service,
            user_gateway=user_gateway,
            current_user=current_user,
        )
        visitor = MagicMock()
        request = ListDirectoryContentRequest(
            project_id=ProjectId(project_uuid),
            parent_id=DirectoryId(directory_uuid),
        )

        with pytest.raises(AccessDeniedError):
            await use_case(visitor, request, _project_unit_list_params())

        visitor.visit_sequence.assert_not_called()

    asyncio.run(scenario())


def test_create_content_ticket_returns_response_when_read_allowed() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000021"
        document_uuid: str = "00000000-0000-4000-8000-000000000022"
        content_uuid: str = "00000000-0000-4000-8000-000000000023"
        now: datetime = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

        current_user = SimpleNamespace(
            id_="00000000-0000-4000-8000-000000000024", name="Alice"
        )
        found_document = SimpleNamespace(
            id_=document_uuid,
            content_ref=SimpleNamespace(value=content_uuid),
        )
        pinned_project = SimpleNamespace(id_=project_uuid)

        context = SimpleNamespace(
            current_user=current_user,
            pinned_project=pinned_project,
            found_document=found_document,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.READ},
                denied=set(),
            )
        )
        ticket_entity = SimpleNamespace(
            id_=SimpleNamespace(value="00000000-0000-4000-8000-000000000025"),
            username=Name("Alice"),
            user_id=UserId("00000000-0000-4000-8000-000000000024"),
            content_ref=found_document.content_ref,
            permissions=[ProjectUnitAction.READ],
            issued_at=SimpleNamespace(),
            expire_at=SimpleNamespace(),
        )
        content_ticket_service = SimpleNamespace(
            create_ticket=MagicMock(return_value=ticket_entity),
        )
        clock = SimpleNamespace(now=lambda: now)

        use_case = CreateContentTicketUsecase(
            clock=clock,
            context_service=context_service,
            permission_service=permission_service,
            content_ticket_service=content_ticket_service,
            group_queries=SimpleNamespace(by_id=AsyncMock()),
        )
        request = CreateContentTicketRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        result: CreateContentTicketResponse = await use_case(request)

        assert result["ticket_id"] is ticket_entity.id_
        assert result["user_id"] == UserId("00000000-0000-4000-8000-000000000024")
        content_ticket_service.create_ticket.assert_called_once()

    asyncio.run(scenario())


def test_create_content_ticket_raises_when_read_denied() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000031"
        document_uuid: str = "00000000-0000-4000-8000-000000000032"

        context = SimpleNamespace(
            current_user=SimpleNamespace(id_="u1", name="Bob"),
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_document=SimpleNamespace(
                id_=document_uuid,
                content_ref=SimpleNamespace(value="c1"),
            ),
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed=set(),
                denied={ProjectUnitAction.READ},
            )
        )
        content_ticket_service = SimpleNamespace(
            create_ticket=MagicMock(),
        )
        clock = SimpleNamespace(now=lambda: datetime.now(timezone.utc))

        use_case = CreateContentTicketUsecase(
            clock=clock,
            context_service=context_service,
            permission_service=permission_service,
            content_ticket_service=content_ticket_service,
            group_queries=SimpleNamespace(by_id=AsyncMock()),
        )
        request = CreateContentTicketRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        with pytest.raises(AccessDeniedError):
            await use_case(request)

        content_ticket_service.create_ticket.assert_not_called()

    asyncio.run(scenario())


def test_create_content_ticket_includes_team_when_team_id_is_provided() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000411"
        document_uuid: str = "00000000-0000-4000-8000-000000000412"
        group_uuid: str = "00000000-0000-4000-8000-000000000413"
        now: datetime = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

        current_user_id = UserId("00000000-0000-4000-8000-000000000414")
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_=current_user_id, name=Name("Alice")),
            pinned_project=SimpleNamespace(id_=ProjectId(project_uuid)),
            found_document=SimpleNamespace(
                id_=document_uuid,
                content_ref=SimpleNamespace(value="00000000-0000-4000-8000-000000000415"),
            ),
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.READ},
                denied=set(),
            )
        )
        ticket_entity = SimpleNamespace(
            id_=SimpleNamespace(value="00000000-0000-4000-8000-000000000416"),
            username=Name("Alice"),
            user_id=current_user_id,
            content_ref=context.found_document.content_ref,
            permissions=[ProjectUnitAction.READ],
            issued_at=SimpleNamespace(),
            expire_at=SimpleNamespace(),
        )
        content_ticket_service = SimpleNamespace(
            create_ticket=MagicMock(return_value=ticket_entity),
        )
        group = SimpleNamespace(
            id_=ProjectGroupId(group_uuid),
            project_id=ProjectId(project_uuid),
            name=Title("TeamBlue"),
            color=HexColor("#112233"),
            participants=[current_user_id],
        )
        group_queries = SimpleNamespace(by_id=AsyncMock(return_value=group))
        clock = SimpleNamespace(now=lambda: now)

        use_case = CreateContentTicketUsecase(
            clock=clock,
            context_service=context_service,
            permission_service=permission_service,
            content_ticket_service=content_ticket_service,
            group_queries=group_queries,
        )
        request = CreateContentTicketRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
            team_id=ProjectGroupId(group_uuid),
        )

        result: CreateContentTicketResponse = await use_case(request)

        assert result["team_id"] == group.id_
        assert result["team_name"] == group.name
        assert result["team_color"] == group.color
        group_queries.by_id.assert_awaited_once_with(ProjectGroupId(group_uuid))

    asyncio.run(scenario())


def test_create_content_ticket_raises_when_group_not_in_project() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000421"
        other_project_uuid: str = "00000000-0000-4000-8000-000000000422"
        document_uuid: str = "00000000-0000-4000-8000-000000000423"
        group_uuid: str = "00000000-0000-4000-8000-000000000424"

        current_user_id = UserId("00000000-0000-4000-8000-000000000425")
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_=current_user_id, name=Name("Alice")),
            pinned_project=SimpleNamespace(id_=ProjectId(project_uuid)),
            found_document=SimpleNamespace(
                id_=document_uuid,
                content_ref=SimpleNamespace(value="content-1"),
            ),
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.READ},
                denied=set(),
            )
        )
        group = SimpleNamespace(
            id_=ProjectGroupId(group_uuid),
            project_id=ProjectId(other_project_uuid),
            participants=[current_user_id],
        )
        group_queries = SimpleNamespace(by_id=AsyncMock(return_value=group))

        use_case = CreateContentTicketUsecase(
            clock=SimpleNamespace(now=lambda: datetime.now(timezone.utc)),
            context_service=context_service,
            permission_service=permission_service,
            content_ticket_service=SimpleNamespace(create_ticket=MagicMock()),
            group_queries=group_queries,
        )
        request = CreateContentTicketRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
            team_id=ProjectGroupId(group_uuid),
        )

        with pytest.raises(ProjectGroupNotInProjectError):
            await use_case(request)

    asyncio.run(scenario())


def test_create_content_ticket_raises_when_user_not_in_group() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000431"
        document_uuid: str = "00000000-0000-4000-8000-000000000432"
        group_uuid: str = "00000000-0000-4000-8000-000000000433"

        current_user_id = UserId("00000000-0000-4000-8000-000000000434")
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_=current_user_id, name=Name("Alice")),
            pinned_project=SimpleNamespace(id_=ProjectId(project_uuid)),
            found_document=SimpleNamespace(
                id_=document_uuid,
                content_ref=SimpleNamespace(value="content-2"),
            ),
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.READ},
                denied=set(),
            )
        )
        group = SimpleNamespace(
            id_=ProjectGroupId(group_uuid),
            project_id=ProjectId(project_uuid),
            participants=[UserId("00000000-0000-4000-8000-000000000435")],
        )
        group_queries = SimpleNamespace(by_id=AsyncMock(return_value=group))
        ticket_service = SimpleNamespace(create_ticket=MagicMock())

        use_case = CreateContentTicketUsecase(
            clock=SimpleNamespace(now=lambda: datetime.now(timezone.utc)),
            context_service=context_service,
            permission_service=permission_service,
            content_ticket_service=ticket_service,
            group_queries=group_queries,
        )
        request = CreateContentTicketRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
            team_id=ProjectGroupId(group_uuid),
        )

        with pytest.raises(UserNotInProjectGroupError):
            await use_case(request)
        ticket_service.create_ticket.assert_not_called()

    asyncio.run(scenario())


def test_jwt_content_ticket_presenter_keeps_base_payload_without_team() -> None:
    presenter = JwtContentTicketPresenter(algorithm="HS256", private_key="secret")
    now = datetime(2099, 1, 1, tzinfo=timezone.utc)
    exp = datetime(2099, 1, 2, tzinfo=timezone.utc)
    response: CreateContentTicketResponse = {
        "ticket_id": SimpleNamespace(value="ticket-1"),
        "username": Name("Alice"),
        "user_id": UserId("00000000-0000-4000-8000-000000000501"),
        "project_id": "00000000-0000-4000-8000-000000000502",
        "content_ref": ContentId("00000000-0000-4000-8000-000000000503"),
        "permissions": [ProjectUnitAction.READ],
        "issued_at": now,
        "expire_at": exp,
    }

    token = presenter.present(response)
    payload = jwt.decode(
        token,
        key="secret",
        algorithms=["HS256"],
        options={"verify_exp": False, "verify_iat": False},
    )

    assert payload["jti"] == "ticket-1"
    assert payload["usr"] == "Alice"
    assert payload["sub"] == "00000000-0000-4000-8000-000000000501"
    assert payload["grp"] == "00000000-0000-4000-8000-000000000502"
    assert payload["perms"] == [ProjectUnitAction.READ.value]
    assert "tid" not in payload
    assert "tnm" not in payload
    assert "tcl" not in payload


def test_jwt_content_ticket_presenter_appends_team_claims_when_present() -> None:
    presenter = JwtContentTicketPresenter(algorithm="HS256", private_key="secret")
    now = datetime(2099, 1, 1, tzinfo=timezone.utc)
    exp = datetime(2099, 1, 2, tzinfo=timezone.utc)
    response: CreateContentTicketResponse = {
        "ticket_id": SimpleNamespace(value="ticket-2"),
        "username": Name("Alice"),
        "user_id": UserId("00000000-0000-4000-8000-000000000511"),
        "project_id": "00000000-0000-4000-8000-000000000512",
        "content_ref": ContentId("00000000-0000-4000-8000-000000000513"),
        "permissions": [ProjectUnitAction.READ],
        "issued_at": now,
        "expire_at": exp,
        "team_id": ProjectGroupId("00000000-0000-4000-8000-000000000514"),
        "team_name": Title("BlueTeam"),
        "team_color": HexColor("#123abc"),
    }

    token = presenter.present(response)
    payload = jwt.decode(
        token,
        key="secret",
        algorithms=["HS256"],
        options={"verify_exp": False, "verify_iat": False},
    )

    assert payload["tid"] == "00000000-0000-4000-8000-000000000514"
    assert payload["tnm"] == "BlueTeam"
    assert payload["tcl"] == "#123abc"


def test_get_document_content_returns_bytes_for_public_project_without_user() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000033"
        document_uuid: str = "00000000-0000-4000-8000-000000000034"
        content_uuid: str = "00000000-0000-4000-8000-000000000035"
        content_bytes: bytes = b'{"ops":[]}'

        context = SimpleNamespace(
            current_user=None,
            pinned_project=SimpleNamespace(is_private=False),
            found_document=SimpleNamespace(
                id_=document_uuid,
                content_ref=ContentId(content_uuid),
            ),
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock()
        content_queries = SimpleNamespace(
            by_location=AsyncMock(return_value=content_bytes),
        )

        use_case = GetDocumentContentUsecase(
            context_service=context_service,
            permission_service=permission_service,
            content_queries=content_queries,
        )
        request = GetDocumentContentRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        result: bytes = await use_case(request)

        assert result == content_bytes
        permission_service.assert_not_called()
        content_queries.by_location.assert_awaited_once_with(
            ProjectId(project_uuid), ContentId(content_uuid)
        )

    asyncio.run(scenario())


def test_get_document_content_raises_when_private_project_has_no_user() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000036"
        document_uuid: str = "00000000-0000-4000-8000-000000000037"
        content_uuid: str = "00000000-0000-4000-8000-000000000038"

        context = SimpleNamespace(
            current_user=None,
            pinned_project=SimpleNamespace(is_private=True),
            found_document=SimpleNamespace(
                id_=document_uuid,
                content_ref=ContentId(content_uuid),
            ),
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock()
        content_queries = SimpleNamespace(
            by_location=AsyncMock(),
        )

        use_case = GetDocumentContentUsecase(
            context_service=context_service,
            permission_service=permission_service,
            content_queries=content_queries,
        )
        request = GetDocumentContentRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        with pytest.raises(AccessDeniedError):
            await use_case(request)

        permission_service.assert_not_called()
        content_queries.by_location.assert_not_awaited()

    asyncio.run(scenario())


def test_get_document_content_returns_bytes_when_private_read_allowed() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000039"
        document_uuid: str = "00000000-0000-4000-8000-000000000040"
        content_uuid: str = "00000000-0000-4000-8000-000000000041"
        content_bytes: bytes = b"monaco-content"

        current_user = SimpleNamespace(id_="00000000-0000-4000-8000-000000000042")
        pinned_project = SimpleNamespace(is_private=True)
        found_document = SimpleNamespace(
            id_=document_uuid,
            content_ref=ContentId(content_uuid),
        )
        context = SimpleNamespace(
            current_user=current_user,
            pinned_project=pinned_project,
            found_document=found_document,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.READ},
                denied=set(),
            )
        )
        content_queries = SimpleNamespace(
            by_location=AsyncMock(return_value=content_bytes),
        )

        use_case = GetDocumentContentUsecase(
            context_service=context_service,
            permission_service=permission_service,
            content_queries=content_queries,
        )
        request = GetDocumentContentRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        result: bytes = await use_case(request)

        assert result == content_bytes
        permission_service.assert_awaited_once()
        content_queries.by_location.assert_awaited_once_with(
            ProjectId(project_uuid), found_document.content_ref
        )

    asyncio.run(scenario())


def test_create_directory_returns_response_when_write_allowed() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000041"
        parent_uuid: str = "00000000-0000-4000-8000-000000000042"
        grandparent_uuid: str = "00000000-0000-4000-8000-000000000043"
        now: datetime = datetime(2025, 2, 1, 10, 0, 0, tzinfo=timezone.utc)

        parent_directory = SimpleNamespace(
            id_=parent_uuid,
            project=SimpleNamespace(value=project_uuid),
            parent=DirectoryId(grandparent_uuid),
        )
        current_user = SimpleNamespace(id_="00000000-0000-4000-8000-000000000044")
        context = SimpleNamespace(
            current_user=current_user,
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_directory=parent_directory,
            parent_directory=parent_directory,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.WRITE},
                denied=set(),
            )
        )
        new_directory_id = DirectoryId("00000000-0000-4000-8000-000000000045")
        new_directory = SimpleNamespace(id_=new_directory_id)
        directory_service = SimpleNamespace(
            create_directory=MagicMock(return_value=new_directory),
        )
        directory_commands = SimpleNamespace(
            add=AsyncMock(),
        )
        clock = SimpleNamespace(now=lambda: now)

        use_case = CreateDirectoryUsecase(
            clock=clock,
            context_service=context_service,
            permission_service=permission_service,
            directory_service=directory_service,
            directory_commands=directory_commands,
        )
        request = CreateDirectoryRequest(
            project_id=ProjectId(project_uuid),
            parent_id=DirectoryId(parent_uuid),
            name=FileName("child"),
        )

        result = await use_case(request)

        assert result["directory"] is new_directory_id
        assert result["created_by"] == current_user.id_
        directory_commands.add.assert_awaited_once_with(new_directory)

    asyncio.run(scenario())


def test_create_directory_raises_when_write_denied() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000051"
        parent_uuid: str = "00000000-0000-4000-8000-000000000052"
        grandparent_uuid: str = "00000000-0000-4000-8000-000000000053"

        parent_directory = SimpleNamespace(
            id_=parent_uuid,
            project=SimpleNamespace(value=project_uuid),
            parent=DirectoryId(grandparent_uuid),
        )
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_="u1"),
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_directory=parent_directory,
            parent_directory=parent_directory,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed=set(),
                denied={ProjectUnitAction.WRITE},
            )
        )
        directory_service = SimpleNamespace(
            create_directory=MagicMock(),
        )
        directory_commands = SimpleNamespace(
            add=AsyncMock(),
        )
        clock = SimpleNamespace(now=lambda: datetime.now(timezone.utc))

        use_case = CreateDirectoryUsecase(
            clock=clock,
            context_service=context_service,
            permission_service=permission_service,
            directory_service=directory_service,
            directory_commands=directory_commands,
        )
        request = CreateDirectoryRequest(
            project_id=ProjectId(project_uuid),
            parent_id=DirectoryId(parent_uuid),
            name=FileName("blocked"),
        )

        with pytest.raises(AccessDeniedError):
            await use_case(request)

        directory_commands.add.assert_not_awaited()

    asyncio.run(scenario())


def test_create_document_returns_response_when_write_allowed() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000061"
        parent_uuid: str = "00000000-0000-4000-8000-000000000062"
        grandparent_uuid: str = "00000000-0000-4000-8000-000000000063"
        content_uuid: str = "00000000-0000-4000-8000-000000000064"
        now: datetime = datetime(2025, 3, 1, 9, 30, 0, tzinfo=timezone.utc)

        parent_directory = SimpleNamespace(
            id_=parent_uuid,
            project=SimpleNamespace(value=project_uuid),
            parent=DirectoryId(grandparent_uuid),
        )
        current_user = SimpleNamespace(id_="00000000-0000-4000-8000-000000000065")
        context = SimpleNamespace(
            current_user=current_user,
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_directory=parent_directory,
            parent_directory=parent_directory,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.WRITE},
                denied=set(),
            )
        )
        new_doc_id = DocumentId("00000000-0000-4000-8000-000000000066")
        content_ref = SimpleNamespace(value=content_uuid)
        new_document = SimpleNamespace(id_=new_doc_id, content_ref=content_ref)
        document_service = SimpleNamespace(
            create_document=MagicMock(return_value=new_document),
        )
        document_commands = SimpleNamespace(
            add=AsyncMock(),
        )
        clock = SimpleNamespace(now=lambda: now)

        use_case = CreateDocumentUsecase(
            clock=clock,
            context_service=context_service,
            permission_service=permission_service,
            document_service=document_service,
            document_commands=document_commands,
        )
        request = CreateDocumentRequest(
            project_id=ProjectId(project_uuid),
            parent_id=DirectoryId(parent_uuid),
            name=FileName("notes.txt"),
        )

        result = await use_case(request)

        assert result["document"] is new_doc_id
        assert result["content_ref"] is content_ref
        document_commands.add.assert_awaited_once_with(new_document)

    asyncio.run(scenario())


def test_create_document_raises_when_write_denied() -> None:
    async def scenario() -> None:
        project_uuid: str = "00000000-0000-4000-8000-000000000071"
        parent_uuid: str = "00000000-0000-4000-8000-000000000072"
        grandparent_uuid: str = "00000000-0000-4000-8000-000000000073"

        parent_directory = SimpleNamespace(
            id_=parent_uuid,
            project=SimpleNamespace(value=project_uuid),
            parent=DirectoryId(grandparent_uuid),
        )
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_="u1"),
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_directory=parent_directory,
            parent_directory=parent_directory,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed=set(),
                denied={ProjectUnitAction.WRITE},
            )
        )
        document_service = SimpleNamespace(
            create_document=MagicMock(),
        )
        document_commands = SimpleNamespace(
            add=AsyncMock(),
        )
        clock = SimpleNamespace(now=lambda: datetime.now(timezone.utc))

        use_case = CreateDocumentUsecase(
            clock=clock,
            context_service=context_service,
            permission_service=permission_service,
            document_service=document_service,
            document_commands=document_commands,
        )
        request = CreateDocumentRequest(
            project_id=ProjectId(project_uuid),
            parent_id=DirectoryId(parent_uuid),
            name=FileName("blocked.txt"),
        )

        with pytest.raises(AccessDeniedError):
            await use_case(request)

        document_commands.add.assert_not_awaited()

    asyncio.run(scenario())


def test_delete_document_returns_message_when_document_not_found() -> None:
    async def scenario() -> None:
        context_service = AsyncMock(side_effect=DocumentNotFoundError())
        permission_service = AsyncMock()
        document_commands = SimpleNamespace(
            delete=AsyncMock(),
        )

        use_case = DeleteDocumentUsecase(
            context_service=context_service,
            permission_service=permission_service,
            document_commands=document_commands,
        )
        request = DeleteDocumentRequest(
            project_id=ProjectId("00000000-0000-4000-8000-000000000081"),
            document_id=DocumentId("00000000-0000-4000-8000-000000000082"),
        )

        response: DeleteDocumentResponse = await use_case(request)

        assert response.deleted is False
        assert response.content_ids == ()
        assert response.message == "Document is already deleted or never been in system"
        document_commands.delete.assert_not_awaited()

    asyncio.run(scenario())


def test_delete_document_deletes_when_write_allowed() -> None:
    async def scenario() -> None:
        parent_uuid: str = "00000000-0000-4000-8000-000000000091"
        document_uuid: str = "00000000-0000-4000-8000-000000000092"
        project_uuid: str = "00000000-0000-4000-8000-000000000093"
        content_uuid: str = "00000000-0000-4000-8000-000000000094"

        found_document = SimpleNamespace(
            id_=DocumentId(document_uuid),
            parent=DirectoryId(parent_uuid),
            content_ref=ContentId(content_uuid),
        )
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_="u1"),
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_document=found_document,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.WRITE},
                denied=set(),
            )
        )
        document_commands = SimpleNamespace(
            delete=AsyncMock(),
        )

        use_case = DeleteDocumentUsecase(
            context_service=context_service,
            permission_service=permission_service,
            document_commands=document_commands,
        )
        request = DeleteDocumentRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        response: DeleteDocumentResponse = await use_case(request)

        assert response.deleted is True
        assert response.content_ids == (ContentId(content_uuid),)
        assert response.message == "Document deleted"
        document_commands.delete.assert_awaited_once_with(found_document.id_)

    asyncio.run(scenario())


def test_delete_document_raises_when_write_denied() -> None:
    async def scenario() -> None:
        parent_uuid: str = "00000000-0000-4000-8000-000000000101"
        document_uuid: str = "00000000-0000-4000-8000-000000000102"
        project_uuid: str = "00000000-0000-4000-8000-000000000103"

        found_document = SimpleNamespace(
            id_=DocumentId(document_uuid),
            parent=DirectoryId(parent_uuid),
        )
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_="u1"),
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_document=found_document,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed=set(),
                denied={ProjectUnitAction.WRITE},
            )
        )
        document_commands = SimpleNamespace(
            delete=AsyncMock(),
        )

        use_case = DeleteDocumentUsecase(
            context_service=context_service,
            permission_service=permission_service,
            document_commands=document_commands,
        )
        request = DeleteDocumentRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        with pytest.raises(AccessDeniedError):
            await use_case(request)

        document_commands.delete.assert_not_awaited()

    asyncio.run(scenario())


def test_delete_directory_returns_message_when_directory_not_found() -> None:
    async def scenario() -> None:
        context_service = AsyncMock(side_effect=DirectoryNotFoundError())
        permission_service = AsyncMock()
        directory_commands = SimpleNamespace(delete=AsyncMock())
        directory_service = SimpleNamespace(is_root=MagicMock())

        use_case = DeleteDirectoryUsecase(
            context_service=context_service,
            permission_service=permission_service,
            directory_commands=directory_commands,
            directory_service=directory_service,
        )
        request = DeleteDirectoryRequest(
            project_id=ProjectId("00000000-0000-4000-8000-000000000111"),
            directory_id=DirectoryId("00000000-0000-4000-8000-000000000112"),
        )

        response: DeleteDirectoryResponse = await use_case(request)
        assert response.deleted is False
        assert response.content_ids == ()
        assert response.message == "Directory is already deleted or never been in system"
        directory_commands.delete.assert_not_awaited()

    asyncio.run(scenario())


def test_delete_directory_returns_deleted_content_ids() -> None:
    async def scenario() -> None:
        parent_uuid: str = "00000000-0000-4000-8000-000000000131"
        directory_uuid: str = "00000000-0000-4000-8000-000000000132"
        project_uuid: str = "00000000-0000-4000-8000-000000000133"
        first_content_uuid: str = "00000000-0000-4000-8000-000000000134"
        second_content_uuid: str = "00000000-0000-4000-8000-000000000135"

        found_directory = SimpleNamespace(
            id_=DirectoryId(directory_uuid),
            parent=DirectoryId(parent_uuid),
        )
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_="u1"),
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_directory=found_directory,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed={ProjectUnitAction.WRITE},
                denied=set(),
            )
        )
        directory_commands = SimpleNamespace(
            delete=AsyncMock(
                return_value=[
                    ContentId(first_content_uuid),
                    ContentId(second_content_uuid),
                ]
            )
        )
        directory_service = SimpleNamespace(is_root=MagicMock(return_value=False))

        use_case = DeleteDirectoryUsecase(
            context_service=context_service,
            permission_service=permission_service,
            directory_commands=directory_commands,
            directory_service=directory_service,
        )
        request = DeleteDirectoryRequest(
            project_id=ProjectId(project_uuid),
            directory_id=DirectoryId(directory_uuid),
        )

        response: DeleteDirectoryResponse = await use_case(request)

        assert response.deleted is True
        assert response.content_ids == (
            ContentId(first_content_uuid),
            ContentId(second_content_uuid),
        )
        assert response.message == "Directory deleted"
        directory_commands.delete.assert_awaited_once_with(found_directory.id_)

    asyncio.run(scenario())


def test_delete_directory_raises_when_write_denied() -> None:
    async def scenario() -> None:
        parent_uuid: str = "00000000-0000-4000-8000-000000000121"
        directory_uuid: str = "00000000-0000-4000-8000-000000000122"
        project_uuid: str = "00000000-0000-4000-8000-000000000123"

        found_directory = SimpleNamespace(id_=directory_uuid, parent=DirectoryId(parent_uuid))
        context = SimpleNamespace(
            current_user=SimpleNamespace(id_="u1"),
            pinned_project=SimpleNamespace(id_=project_uuid),
            found_directory=found_directory,
        )
        context_service = AsyncMock(return_value=context)
        permission_service = AsyncMock(
            return_value=ResolvedUnitPermissions(
                allowed=set(),
                denied={ProjectUnitAction.WRITE},
            )
        )
        directory_commands = SimpleNamespace(delete=AsyncMock())
        directory_service = SimpleNamespace(is_root=MagicMock(return_value=False))

        use_case = DeleteDirectoryUsecase(
            context_service=context_service,
            permission_service=permission_service,
            directory_commands=directory_commands,
            directory_service=directory_service,
        )
        request = DeleteDirectoryRequest(
            project_id=ProjectId(project_uuid),
            directory_id=DirectoryId(directory_uuid),
        )

        with pytest.raises(AccessDeniedError):
            await use_case(request)
        directory_commands.delete.assert_not_awaited()

    asyncio.run(scenario())


def test_delete_document_composition_adds_task_for_deleted_content() -> None:
    async def scenario() -> None:
        now: datetime = datetime(2026, 3, 29, tzinfo=timezone.utc)
        project_uuid: str = "00000000-0000-4000-8000-000000000141"
        document_uuid: str = "00000000-0000-4000-8000-000000000142"
        content_uuid: str = "00000000-0000-4000-8000-000000000143"

        created_task = SimpleNamespace(name="task")
        clock = SimpleNamespace(now=MagicMock(return_value=now))
        use_case = AsyncMock(
            return_value=DeleteDocumentResponse(
                project_id=ProjectId(project_uuid),
                content_ids=(ContentId(content_uuid),),
                deleted=True,
                message="Document deleted",
            )
        )
        unit_of_work = AsyncMock()
        unit_of_work.__aenter__.return_value = None
        unit_of_work.__aexit__.return_value = None
        task_service = SimpleNamespace(create_task=MagicMock(return_value=created_task))
        task_gateway = SimpleNamespace(add=AsyncMock())
        composition = DeleteDocumentComposition(
            clock=clock,
            usecase=use_case,
            unit_of_work=unit_of_work,
            task_service=task_service,
            task_gateway=task_gateway,
        )
        request = DeleteDocumentRequest(
            project_id=ProjectId(project_uuid),
            document_id=DocumentId(document_uuid),
        )

        await composition(request)

        task_service.create_task.assert_called_once_with(
            "documents.deleted",
            {
                "content_ids": [content_uuid],
                "group": project_uuid,
            },
            now=now,
        )
        task_gateway.add.assert_awaited_once_with(created_task)

    asyncio.run(scenario())


def test_delete_directory_composition_skips_task_when_nothing_deleted() -> None:
    async def scenario() -> None:
        now: datetime = datetime(2026, 3, 29, tzinfo=timezone.utc)
        project_uuid: str = "00000000-0000-4000-8000-000000000151"
        directory_uuid: str = "00000000-0000-4000-8000-000000000152"

        clock = SimpleNamespace(now=MagicMock(return_value=now))
        use_case = AsyncMock(
            return_value=DeleteDirectoryResponse(
                project_id=ProjectId(project_uuid),
                content_ids=(),
                deleted=False,
                message="Directory is already deleted or never been in system",
            )
        )
        unit_of_work = AsyncMock()
        unit_of_work.__aenter__.return_value = None
        unit_of_work.__aexit__.return_value = None
        task_service = SimpleNamespace(create_task=MagicMock())
        task_gateway = SimpleNamespace(add=AsyncMock())
        composition = DeleteDirectoryComposition(
            clock=clock,
            usecase=use_case,
            unit_of_work=unit_of_work,
            task_service=task_service,
            task_gateway=task_gateway,
        )
        request = DeleteDirectoryRequest(
            project_id=ProjectId(project_uuid),
            directory_id=DirectoryId(directory_uuid),
        )

        await composition(request)

        task_service.create_task.assert_not_called()
        task_gateway.add.assert_not_awaited()

    asyncio.run(scenario())
