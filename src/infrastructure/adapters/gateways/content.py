import httpx

from domain.entities import ProjectId
from domain.entities.document import ContentId
from application.ports.gateways import ContentQueryGateway, GatewayFailedError
from setup.config import Settings


class HttpContentQueryGateway(ContentQueryGateway):

    def __init__(self, settings: Settings):
        self._base_url: str = settings.collaboration.base_url.rstrip("/")
        self._content_path: str = settings.collaboration.content_path
        self._timeout_seconds: float = settings.collaboration.timeout_seconds

    async def by_location(
        self, project_id: ProjectId, content_id: ContentId
    ) -> bytes:
        path: str = self._content_path.format(
            group_id=project_id.value,
            content_id=content_id.value,
        )
        url: str = f"{self._base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response: httpx.Response = await client.get(url)
                response.raise_for_status()
        except (httpx.HTTPError, ValueError) as error:
            raise GatewayFailedError(
                "Cannot get document content: collaboration service is unavailable"
            ) from error

        return response.content
