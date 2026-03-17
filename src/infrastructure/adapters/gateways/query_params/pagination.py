from sqlalchemy import Select

from application.ports.gateways.query_params import (
    OffsetPagination,
    CreationPagination,
    NamePagination,
    PaginationVisitor,
)
from .base import OrderableColumn, ColumnResolver


class SQLAlchemyPaginationApplier(PaginationVisitor[Select]):

    def __init__(
        self,
        query: Select,
        resolve_column: ColumnResolver,
    ) -> None:
        self._query: Select = query
        self._resolve_column: ColumnResolver = resolve_column

    def visit_offset(self, pagination: OffsetPagination) -> Select:
        return self._query.limit(pagination.limit).offset(pagination.offset)

    def _apply_cursor[TCursor](
        self,
        domain_field: str,
        cursor: TCursor | None,
        limit: int,
        order_field: str = "id_",
    ) -> Select:
        col: OrderableColumn = self._resolve_column(domain_field)
        order_col: OrderableColumn = self._resolve_column(order_field)
        query: Select = self._query

        if cursor is not None:
            query = query.where(col > cursor)

        return query.order_by(col.asc(), order_col.asc()).limit(limit)

    def visit_created_at(self, pagination: CreationPagination) -> Select:
        return self._apply_cursor(
            domain_field="created_at",
            cursor=pagination.latest_creation,
            limit=pagination.limit,
        )

    def visit_name(self, pagination: NamePagination) -> Select:
        return self._apply_cursor(
            domain_field="name",
            cursor=pagination.latest_name,
            limit=pagination.limit,
        )
