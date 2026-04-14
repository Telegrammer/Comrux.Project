# Этот тест усиливает protection и refactor-resistance для export infrastructure.
# target_file: src/tests/test_project_release_infrastructure.py — проверка сборки архива релиза и порядка snapshot-обхода дерева.

from __future__ import annotations

import asyncio
import io
import json
import zipfile
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import cast
from uuid import UUID

from domain.entities.project import ProjectId
from domain.entities.user import UserId
from domain.enums import ProjectUnitType
from domain.export import ProjectReleaseId, ProjectReleaseService
from infrastructure.export.gateways import SqlAlchemyProjectTreeSnapshotGateway
from infrastructure.export.storage import ReleaseStorageKeys, S3ProjectReleaseArtifactGateway

from application.export import ProjectTreeNodeSnapshot, PublishedGroupContent


class FakeScalarResult:
    def __init__(self, nodes: list[SimpleNamespace]) -> None:
        self._nodes = nodes

    def all(self) -> list[SimpleNamespace]:
        return self._nodes


class FakeExecuteResult:
    def __init__(self, nodes: list[SimpleNamespace]) -> None:
        self._nodes = nodes

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self._nodes)


class FakeAsyncSession:
    def __init__(self, nodes: list[SimpleNamespace]) -> None:
        self._nodes = nodes

    async def execute(self, statement: object) -> FakeExecuteResult:
        del statement
        return FakeExecuteResult(self._nodes)


class FakeS3Client:
    def __init__(self) -> None:
        self.put_calls: list[dict[str, object]] = []

    async def __aenter__(self) -> "FakeS3Client":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type
        del exc
        del tb

    async def put_object(self, **kwargs: object) -> None:
        self.put_calls.append(kwargs)


class FakeS3ProjectReleaseArtifactGateway(S3ProjectReleaseArtifactGateway):
    def __init__(self, client: FakeS3Client) -> None:
        self._bucket = "releases"
        self._client = client

    def _create_client(self) -> FakeS3Client:
        return self._client


def _release(now: datetime):
    return ProjectReleaseService(
        id_generator=lambda: ProjectReleaseId("550e8400-e29b-41d4-a716-446655440099")
    ).create_release(
        project_id=ProjectId("550e8400-e29b-41d4-a716-446655440001"),
        requested_by=UserId("550e8400-e29b-41d4-a716-446655440002"),
        name="First release",
        now=now,
    )


def test_project_release_artifact_gateway_builds_archive_and_metadata() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc)
        client = FakeS3Client()
        gateway = FakeS3ProjectReleaseArtifactGateway(client)

        artifact = await gateway.build_and_store(
            release=_release(now),
            tree=[
                ProjectTreeNodeSnapshot(path="src", unit_type="DIR"),
                ProjectTreeNodeSnapshot(
                    path="src/main.py",
                    unit_type="DOC",
                    content_ref="550e8400-e29b-41d4-a716-446655440010",
                ),
            ],
            contents=[
                PublishedGroupContent(
                    content_id="550e8400-e29b-41d4-a716-446655440010",
                    content=b"print('hello')\n",
                )
            ],
            finished_at=now,
        )

        assert artifact.artifact_key == ReleaseStorageKeys.archive(
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440099",
        )
        assert artifact.file_name == "First-release.zip"
        assert len(client.put_calls) == 2

        archive_call = client.put_calls[0]
        archive_body = cast(bytes, archive_call["Body"])
        archive = zipfile.ZipFile(io.BytesIO(archive_body))

        assert archive_call["Bucket"] == "releases"
        assert archive_call["Key"] == artifact.artifact_key
        assert archive.namelist() == ["src/", "src/main.py"]
        assert archive.read("src/main.py") == b"print('hello')\n"

        metadata_call = client.put_calls[1]
        metadata = json.loads(cast(bytes, metadata_call["Body"]).decode())

        assert metadata_call["Key"] == ReleaseStorageKeys.meta(
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440099",
        )
        assert metadata["status"] == "READY"
        assert metadata["file_name"] == "First-release.zip"
        assert metadata["size"] == artifact.archive_size

    asyncio.run(scenario())


def test_project_tree_snapshot_gateway_preserves_tree_order_iteratively() -> None:
    async def scenario() -> None:
        root_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        src_id = UUID("550e8400-e29b-41d4-a716-446655440002")

        nodes = [
            SimpleNamespace(
                id_=root_id,
                parent_id=None,
                name="",
                unit_type=ProjectUnitType.DIRECTORY,
                attributes={},
            ),
            SimpleNamespace(
                id_=src_id,
                parent_id=root_id,
                name="src",
                unit_type=ProjectUnitType.DIRECTORY,
                attributes={},
            ),
            SimpleNamespace(
                id_=UUID("550e8400-e29b-41d4-a716-446655440003"),
                parent_id=src_id,
                name="a.py",
                unit_type=ProjectUnitType.DOCUMENT,
                attributes={"content_ref": "a-content"},
            ),
            SimpleNamespace(
                id_=UUID("550e8400-e29b-41d4-a716-446655440004"),
                parent_id=src_id,
                name="b.py",
                unit_type=ProjectUnitType.DOCUMENT,
                attributes={"content_ref": "b-content"},
            ),
            SimpleNamespace(
                id_=UUID("550e8400-e29b-41d4-a716-446655440005"),
                parent_id=root_id,
                name="z.md",
                unit_type=ProjectUnitType.DOCUMENT,
                attributes={"content_ref": "z-content"},
            ),
        ]
        gateway = SqlAlchemyProjectTreeSnapshotGateway(FakeAsyncSession(nodes))

        snapshots = await gateway.by_project(
            ProjectId("550e8400-e29b-41d4-a716-446655440010")
        )

        assert snapshots == [
            ProjectTreeNodeSnapshot(path="src", unit_type="DIR", content_ref=None),
            ProjectTreeNodeSnapshot(
                path="src/a.py",
                unit_type="DOC",
                content_ref="a-content",
            ),
            ProjectTreeNodeSnapshot(
                path="src/b.py",
                unit_type="DOC",
                content_ref="b-content",
            ),
            ProjectTreeNodeSnapshot(
                path="z.md",
                unit_type="DOC",
                content_ref="z-content",
            ),
        ]

    asyncio.run(scenario())
