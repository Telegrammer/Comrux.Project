from __future__ import annotations

import asyncio
import io
import json
import re
import zipfile
from collections.abc import Sequence
from datetime import datetime

from application.export import (
    ProjectReleaseArtifactGateway,
    ProjectReleaseDownload,
    ProjectTreeNodeSnapshot,
    PublishedGroupContent,
    StoredProjectReleaseArtifact,
)
from domain.export import ProjectRelease
from setup.config import Settings
from utils import unwrap_value


class ReleaseStorageKeys:
    @staticmethod
    def archive(project_id: str, release_id: str) -> str:
        return f"{project_id}/{release_id}/archive.zip"

    @staticmethod
    def meta(project_id: str, release_id: str) -> str:
        return f"{project_id}/{release_id}/meta.json"


def _to_file_name(release_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", release_name.strip()).strip("-")
    if normalized == "":
        normalized = "release"
    return f"{normalized}.zip"


def _build_archive_bytes(
    tree: Sequence[ProjectTreeNodeSnapshot],
    content_by_id: dict[str, bytes],
) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for node in tree:
            if node.path == "":
                continue
            if node.content_ref is None:
                archive.writestr(f"{node.path.rstrip('/')}/", b"")
                continue
            content = content_by_id.get(node.content_ref)
            if content is None:
                raise FileNotFoundError(
                    f"Published content {node.content_ref} is missing for release"
                )
            archive.writestr(node.path, content)
    return buffer.getvalue()


class S3ProjectReleaseArtifactGateway(ProjectReleaseArtifactGateway):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._bucket = settings.storage.releases_bucket

    async def build_and_store(
        self,
        release: ProjectRelease,
        tree: Sequence[ProjectTreeNodeSnapshot],
        contents: Sequence[PublishedGroupContent],
        finished_at: datetime,
    ) -> StoredProjectReleaseArtifact:
        content_by_id = {item.content_id: item.content for item in contents}
        archive_key = ReleaseStorageKeys.archive(
            str(unwrap_value(release.project_id)),
            str(unwrap_value(release.id_)),
        )
        meta_key = ReleaseStorageKeys.meta(
            str(unwrap_value(release.project_id)),
            str(unwrap_value(release.id_)),
        )
        file_name = _to_file_name(release.name)
        archive_bytes = await asyncio.to_thread(
            _build_archive_bytes,
            tree,
            content_by_id,
        )

        metadata = {
            "release_id": str(unwrap_value(release.id_)),
            "project_id": str(unwrap_value(release.project_id)),
            "name": release.name,
            "status": "READY",
            "file_name": file_name,
            "size": len(archive_bytes),
            "created_at": unwrap_value(release.created_at).isoformat(),
            "finished_at": finished_at.isoformat(),
        }

        async with self._create_client() as client:
            await client.put_object(
                Bucket=self._bucket,
                Key=archive_key,
                Body=archive_bytes,
                ContentType="application/zip",
            )
            await client.put_object(
                Bucket=self._bucket,
                Key=meta_key,
                Body=json.dumps(metadata).encode(),
                ContentType="application/json",
            )
        return StoredProjectReleaseArtifact(
            artifact_key=archive_key,
            file_name=file_name,
            archive_size=len(archive_bytes),
        )

    async def download(
        self,
        release: ProjectRelease,
    ) -> ProjectReleaseDownload:
        if release.artifact_key is None or release.file_name is None:
            raise FileNotFoundError("Release artifact is not available")

        async with self._create_client() as client:
            try:
                response = await client.get_object(
                    Bucket=self._bucket,
                    Key=release.artifact_key,
                )
            except Exception as error:
                if getattr(error, "response", {}).get("Error", {}).get("Code") in (
                    "NoSuchKey",
                    "404",
                ):
                    raise FileNotFoundError("Release artifact was not found") from error
                raise
            content = await response["Body"].read()
        return ProjectReleaseDownload(
            file_name=release.file_name,
            media_type="application/zip",
            content=content,
        )

    def _create_client(self):
        from aiobotocore.session import get_session

        return get_session().create_client(
            service_name="s3",
            endpoint_url=self._settings.storage.s3_endpoint_url,
            aws_access_key_id=self._settings.storage.s3_access_key,
            aws_secret_access_key=self._settings.storage.s3_secret_key,
            region_name=self._settings.storage.s3_region,
        )
