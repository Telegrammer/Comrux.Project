from abc import abstractmethod
from typing import Protocol

from domain.entities import ProjectId
from domain.entities.document import ContentId


class ContentQueryGateway(Protocol):

    @abstractmethod
    async def by_location(
        self, project_id: ProjectId, content_id: ContentId
    ) -> bytes:
        raise NotImplementedError
