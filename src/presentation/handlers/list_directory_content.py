import logging

from pydantic import UUID4
from application.usecases import (
    ListDirectoryContentRequest,
)
from application.compositions import ListDirectoryContentCompostion
from application.ports.gateways.query_params import (
    OffsetPagination,
    ProjectUnitListParams,
)
from presentation.presenters import PydanticProjectUnitVisitor, OrdersPresenter
from presentation.models import DirectoryRead, DocumentRead

logger = logging.getLogger(__name__)


# TODO: fix cursor workflow
class ListDirectoryContentHandler:

    def __init__(
        self,
        usecase: ListDirectoryContentCompostion,
        unit_visitor: PydanticProjectUnitVisitor,
        orders_presenter: OrdersPresenter,
    ):
        self._usecase: ListDirectoryContentCompostion = usecase
        self._unit_visitor: PydanticProjectUnitVisitor = unit_visitor
        self._orders_presenter: OrdersPresenter = orders_presenter

    async def __call__(
        self,
        project_id: UUID4,
        directory_id: UUID4,
        offset: int,
        limit: int,
        raw_orders: str,
    ) -> list[DirectoryRead, DocumentRead]:

        await self._usecase(
            self._unit_visitor,
            ListDirectoryContentRequest.from_primitives(
                project=str(project_id), parent=str(directory_id)
            ),
            ProjectUnitListParams(
                OffsetPagination(offset, limit), self._orders_presenter(raw_orders)
            ),
        )

        content: list[DirectoryRead | DocumentRead] = self._unit_visitor.get_visited()
        return content
