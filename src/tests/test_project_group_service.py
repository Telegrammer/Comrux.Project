import pytest
from datetime import datetime, timezone

from domain.entities import Project, ProjectGroup, ProjectGroupId, ProjectId, UserId
from domain.enums import ProjectRole
from domain.exceptions import (
    ProjectGroupAdmissionError,
    ProjectGroupDuplicateParticipantError,
    ProjectGroupOwnerInParticipantsError,
    ProjectGroupParticipantNotInProjectError,
)
from domain.services import ProjectGroupService
from domain.value_objects import HexColor, PassedDatetime, Title


def _service() -> ProjectGroupService:
    return ProjectGroupService(
        id_generator=lambda: ProjectGroupId("550e8400-e29b-41d4-a716-446655440001")
    )


def _project(owner_id: str, member_ids: list[str]) -> Project:
    now = datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc)
    members = {UserId(owner_id): ProjectRole.OWNER}
    for member_id in member_ids:
        members[UserId(member_id)] = ProjectRole.MEMBER
    return Project(
        id_=ProjectId("550e8400-e29b-41d4-a716-446655440002"),
        title=Title("Demo"),
        root_directory=None,
        description="",
        members=members,
        created_at=PassedDatetime(now, now),
        is_private=False,
    )


def test_create_group_raises_if_participants_have_duplicates() -> None:
    service = _service()
    project = _project(
        owner_id="550e8400-e29b-41d4-a716-446655440003",
        member_ids=["550e8400-e29b-41d4-a716-446655440004"],
    )

    with pytest.raises(ProjectGroupDuplicateParticipantError):
        service.create_group(
            name=Title("Backend"),
            color=HexColor("#112233"),
            project=project,
            owner=UserId("550e8400-e29b-41d4-a716-446655440003"),
            participants=[
                UserId("550e8400-e29b-41d4-a716-446655440004"),
                UserId("550e8400-e29b-41d4-a716-446655440004"),
            ],
            is_public=False,
        )


def test_create_group_raises_if_participant_not_in_project() -> None:
    service = _service()
    project = _project(
        owner_id="550e8400-e29b-41d4-a716-446655440003",
        member_ids=[],
    )

    with pytest.raises(ProjectGroupParticipantNotInProjectError):
        service.create_group(
            name=Title("Backend"),
            color=HexColor("#112233"),
            project=project,
            owner=UserId("550e8400-e29b-41d4-a716-446655440003"),
            participants=[
                UserId("550e8400-e29b-41d4-a716-446655440099"),
            ],
            is_public=False,
        )


def test_create_group_adds_owner_if_missing() -> None:
    service = _service()
    owner = "550e8400-e29b-41d4-a716-446655440003"
    member = "550e8400-e29b-41d4-a716-446655440004"
    project = _project(owner_id=owner, member_ids=[member])

    group = service.create_group(
        name=Title("Backend"),
        color=HexColor("#112233"),
        project=project,
        owner=UserId(owner),
        participants=[
            UserId(member),
        ],
        is_public=False,
    )

    assert UserId(owner) in group.participants
    assert len(group.participants) == 2


def test_create_group_raises_if_owner_is_in_requested_participants() -> None:
    service = _service()
    owner = "550e8400-e29b-41d4-a716-446655440003"
    member = "550e8400-e29b-41d4-a716-446655440004"
    project = _project(owner_id=owner, member_ids=[member])

    with pytest.raises(ProjectGroupOwnerInParticipantsError):
        service.create_group(
            name=Title("Backend"),
            color=HexColor("#112233"),
            project=project,
            owner=UserId(owner),
            participants=[UserId(owner), UserId(member)],
            is_public=False,
        )


def test_join_private_group_requires_owner_admission() -> None:
    service = _service()
    group = ProjectGroup(
        id_=ProjectGroupId("550e8400-e29b-41d4-a716-446655440010"),
        project_id=ProjectId("550e8400-e29b-41d4-a716-446655440011"),
        name=Title("Core"),
        color=HexColor("#112233"),
        owner=UserId("550e8400-e29b-41d4-a716-446655440012"),
        is_public=False,
        participants=[],
    )

    with pytest.raises(ProjectGroupAdmissionError):
        service.join(
            group=group,
            participant_id=UserId("550e8400-e29b-41d4-a716-446655440013"),
            actor_id=UserId("550e8400-e29b-41d4-a716-446655440013"),
        )


def test_join_public_group_denies_adding_another_participant_by_non_owner() -> None:
    service = _service()
    group = ProjectGroup(
        id_=ProjectGroupId("550e8400-e29b-41d4-a716-446655440014"),
        project_id=ProjectId("550e8400-e29b-41d4-a716-446655440015"),
        name=Title("Open"),
        color=HexColor("#112233"),
        owner=UserId("550e8400-e29b-41d4-a716-446655440016"),
        is_public=True,
        participants=[],
    )

    with pytest.raises(ProjectGroupAdmissionError):
        service.join(
            group=group,
            participant_id=UserId("550e8400-e29b-41d4-a716-446655440017"),
            actor_id=UserId("550e8400-e29b-41d4-a716-446655440018"),
        )


def test_owner_may_leave_group_when_owner_and_participation_are_independent() -> None:
    service = _service()
    owner = UserId("550e8400-e29b-41d4-a716-446655440022")
    group = ProjectGroup(
        id_=ProjectGroupId("550e8400-e29b-41d4-a716-446655440020"),
        project_id=ProjectId("550e8400-e29b-41d4-a716-446655440021"),
        name=Title("Design"),
        color=HexColor("#112233"),
        owner=owner,
        is_public=True,
        participants=[
            owner,
            UserId("550e8400-e29b-41d4-a716-446655440023"),
        ],
    )

    updated = service.leave(group, owner)

    assert str(updated.owner) == owner.value
    assert owner not in updated.participants
