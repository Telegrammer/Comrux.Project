# Этот тест усиливает protection и refactor-resistance для сценариев создания и сборки project release.
# target_file: src/tests/test_project_release_usecases.py — проверка create release composition и build release composition.

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

from application.export import (
    BuildProjectReleaseComposition,
    CreateProjectReleaseComposition,
    CreateProjectReleaseRequest,
    CreateProjectReleaseUsecase,
    ProjectTreeNodeSnapshot,
    PublishedGroupContent,
    StoredProjectReleaseArtifact,
)
from application.ports.gateways.errors import GatewayFailedError
from domain.entities import UserId
from domain.entities.project import Project, ProjectId
from domain.enums import ProjectRole
from domain.export import (
    ProjectRelease,
    ProjectReleaseId,
    ProjectReleaseService,
    ProjectReleaseStatus,
)
from domain.value_objects import PassedDatetime, Title


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FakeCurrentUserService:
    def __init__(self, user_id: str) -> None:
        self._user_id = user_id

    async def __call__(self):
        return type("CurrentUser", (), {"id_": self._user_id})()


class FakeProjectQueryGateway:
    def __init__(self, project: Project) -> None:
        self._project = project

    async def by_id(self, project_id: ProjectId) -> Project:
        assert project_id.value == self._project.id_
        return self._project


class FakeReleaseCommandGateway:
    def __init__(self) -> None:
        self.added: list[ProjectRelease] = []
        self.updated: list[ProjectRelease] = []

    async def add(self, release: ProjectRelease) -> None:
        self.added.append(release)

    async def update(self, release: ProjectRelease) -> None:
        self.updated.append(release)


class FakeTaskGateway:
    def __init__(self) -> None:
        self.tasks: list[object] = []

    async def add(self, task: object) -> None:
        self.tasks.append(task)


class FakeUnitOfWork:
    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type
        del exc
        del tb


class FakeReleaseQueryGateway:
    def __init__(self, release: ProjectRelease) -> None:
        self._release = release

    async def by_id(self, release_id) -> ProjectRelease | None:
        assert release_id.value == self._release.id_
        return self._release


class FakeTreeSnapshotGateway:
    async def by_project(self, project_id: ProjectId) -> list[ProjectTreeNodeSnapshot]:
        assert project_id == ProjectId("550e8400-e29b-41d4-a716-446655440001")
        return [
            ProjectTreeNodeSnapshot(path="src", unit_type="DIRECTORY"),
            ProjectTreeNodeSnapshot(
                path="src/main.py",
                unit_type="DOC",
                content_ref="550e8400-e29b-41d4-a716-446655440010",
            ),
        ]


class FakeGroupPublishedContentGateway:
    async def by_group(self, group_id: ProjectId) -> list[PublishedGroupContent]:
        assert group_id == ProjectId("550e8400-e29b-41d4-a716-446655440001")
        return [
            PublishedGroupContent(
                content_id="550e8400-e29b-41d4-a716-446655440010",
                content=b"print('hello')\n",
            )
        ]


class FakeArtifactGateway:
    async def build_and_store(
        self,
        release: ProjectRelease,
        tree: list[ProjectTreeNodeSnapshot],
        contents: list[PublishedGroupContent],
        finished_at: datetime,
    ) -> StoredProjectReleaseArtifact:
        assert release.name == "First release"
        assert len(tree) == 2
        assert len(contents) == 1
        assert finished_at.tzinfo is not None
        return StoredProjectReleaseArtifact(
            artifact_key="550e8400-e29b-41d4-a716-446655440001/release/archive.zip",
            file_name="first-release.zip",
            archive_size=128,
        )

    async def download(self, release: ProjectRelease):
        raise AssertionError("download must not be called in this test")


class FailingArtifactGateway:
    def __init__(self, error: Exception) -> None:
        self._error = error

    async def build_and_store(
        self,
        release: ProjectRelease,
        tree: list[ProjectTreeNodeSnapshot],
        contents: list[PublishedGroupContent],
        finished_at: datetime,
    ) -> StoredProjectReleaseArtifact:
        del release
        del tree
        del contents
        del finished_at
        raise self._error

    async def download(self, release: ProjectRelease):
        del release
        raise AssertionError("download must not be called in this test")


def _project(owner_id: str, now: datetime) -> Project:
    return Project(
        id_=ProjectId("550e8400-e29b-41d4-a716-446655440001"),
        title=Title("Demo_project"),
        description="",
        root_directory=None,
        members={UserId(owner_id): ProjectRole.OWNER},
        created_at=PassedDatetime(now, now),
        is_private=False,
    )


def test_create_project_release_composition_creates_release_and_outbox_task() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc)
        current_user_id = "550e8400-e29b-41d4-a716-446655440002"
        project = _project(current_user_id, now)
        release_commands = FakeReleaseCommandGateway()
        task_gateway = FakeTaskGateway()
        usecase = CreateProjectReleaseUsecase(
            current_user=FakeCurrentUserService(current_user_id),
            project_queries=FakeProjectQueryGateway(project),
            release_service=ProjectReleaseService(
                id_generator=lambda: ProjectReleaseId(
                    "550e8400-e29b-41d4-a716-446655440003"
                )
            ),
            clock=FakeClock(now),
        )
        composition = CreateProjectReleaseComposition(
            clock=FakeClock(now),
            unit_of_work=FakeUnitOfWork(),
            usecase=usecase,
            release_commands=release_commands,
            task_service=type(
                "TaskServiceStub",
                (),
                {
                    "create_task": staticmethod(
                        lambda task_type, payload, now: SimpleNamespace(
                            id_="550e8400-e29b-41d4-a716-446655440004",
                            task_type=task_type,
                            payload=payload,
                            created_at=now,
                        )
                    )
                },
            )(),
            task_gateway=task_gateway,
        )

        release = await composition(
            CreateProjectReleaseRequest.from_primitives(
                project_id=project.id_,
                name="First release",
            )
        )

        assert release.status is ProjectReleaseStatus.CREATED
        assert release_commands.added[0].name == "First release"
        assert task_gateway.tasks[0].task_type == "project.releases.created"
        assert task_gateway.tasks[0].payload == {
            "project_id": project.id_,
            "release_id": "550e8400-e29b-41d4-a716-446655440003",
        }

    asyncio.run(scenario())


def test_build_project_release_composition_marks_release_ready() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 14, 13, 0, tzinfo=timezone.utc)
        release = ProjectReleaseService(
            id_generator=lambda: ProjectReleaseId(
                "550e8400-e29b-41d4-a716-446655440099"
            )
        ).create_release(
            project_id=ProjectId("550e8400-e29b-41d4-a716-446655440001"),
            requested_by=UserId("550e8400-e29b-41d4-a716-446655440002"),
            name="First release",
            now=now,
        )
        release_commands = FakeReleaseCommandGateway()
        composition = BuildProjectReleaseComposition(
            clock=FakeClock(now),
            unit_of_work=FakeUnitOfWork(),
            release_queries=FakeReleaseQueryGateway(release),
            release_commands=release_commands,
            release_service=ProjectReleaseService(
                id_generator=lambda: ProjectReleaseId(
                    "550e8400-e29b-41d4-a716-446655440099"
                )
            ),
            tree_snapshots=FakeTreeSnapshotGateway(),
            group_content=FakeGroupPublishedContentGateway(),
            artifacts=FakeArtifactGateway(),
        )

        await composition(
            project_id="550e8400-e29b-41d4-a716-446655440001",
            release_id=release.id_,
        )

        assert release_commands.updated[0].status is ProjectReleaseStatus.PROCESSING
        assert release_commands.updated[1].status is ProjectReleaseStatus.READY
        assert release_commands.updated[1].artifact_key is not None
        assert release_commands.updated[1].archive_size == 128

    asyncio.run(scenario())


def test_build_project_release_composition_marks_release_failed_with_gateway_error() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 14, 13, 0, tzinfo=timezone.utc)
        release = ProjectReleaseService(
            id_generator=lambda: ProjectReleaseId(
                "550e8400-e29b-41d4-a716-446655440099"
            )
        ).create_release(
            project_id=ProjectId("550e8400-e29b-41d4-a716-446655440001"),
            requested_by=UserId("550e8400-e29b-41d4-a716-446655440002"),
            name="First release",
            now=now,
        )
        release_commands = FakeReleaseCommandGateway()
        composition = BuildProjectReleaseComposition(
            clock=FakeClock(now),
            unit_of_work=FakeUnitOfWork(),
            release_queries=FakeReleaseQueryGateway(release),
            release_commands=release_commands,
            release_service=ProjectReleaseService(
                id_generator=lambda: ProjectReleaseId(
                    "550e8400-e29b-41d4-a716-446655440099"
                )
            ),
            tree_snapshots=FakeTreeSnapshotGateway(),
            group_content=FakeGroupPublishedContentGateway(),
            artifacts=FailingArtifactGateway(
                GatewayFailedError("Cannot list group content: collaboration service is unavailable")
            ),
        )

        await composition(
            project_id="550e8400-e29b-41d4-a716-446655440001",
            release_id=release.id_,
        )

        assert release_commands.updated[0].status is ProjectReleaseStatus.PROCESSING
        assert release_commands.updated[1].status is ProjectReleaseStatus.FAILED
        assert (
            release_commands.updated[1].error_message
            == "Cannot list group content: collaboration service is unavailable"
        )

    asyncio.run(scenario())


def test_build_project_release_composition_masks_unexpected_errors() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 14, 13, 0, tzinfo=timezone.utc)
        release = ProjectReleaseService(
            id_generator=lambda: ProjectReleaseId(
                "550e8400-e29b-41d4-a716-446655440099"
            )
        ).create_release(
            project_id=ProjectId("550e8400-e29b-41d4-a716-446655440001"),
            requested_by=UserId("550e8400-e29b-41d4-a716-446655440002"),
            name="First release",
            now=now,
        )
        release_commands = FakeReleaseCommandGateway()
        composition = BuildProjectReleaseComposition(
            clock=FakeClock(now),
            unit_of_work=FakeUnitOfWork(),
            release_queries=FakeReleaseQueryGateway(release),
            release_commands=release_commands,
            release_service=ProjectReleaseService(
                id_generator=lambda: ProjectReleaseId(
                    "550e8400-e29b-41d4-a716-446655440099"
                )
            ),
            tree_snapshots=FakeTreeSnapshotGateway(),
            group_content=FakeGroupPublishedContentGateway(),
            artifacts=FailingArtifactGateway(RuntimeError("boom")),
        )

        await composition(
            project_id="550e8400-e29b-41d4-a716-446655440001",
            release_id=release.id_,
        )

        assert release_commands.updated[1].status is ProjectReleaseStatus.FAILED
        assert (
            release_commands.updated[1].error_message
            == "Unexpected error while building project release"
        )

    asyncio.run(scenario())
