# infrastructure/persistence/query_builder.py

from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase

from application.ports.gateways.query_params import (
    Pagination,
    SortingParam,
    SortingOrder,
    SearchQuery,
)
from .query_params.base import OrderableColumn
from .query_params.pagination import SQLAlchemyPaginationApplier


class SQLAlchemyQueryBuilder:

    def __init__(
        self,
        field_mapping: dict[str, str] | None = None,
    ) -> None:
        self._model = None
        self._field_mapping = field_mapping or {}

    def _resolve_column(self, domain_field: str) -> OrderableColumn:
        column_name = self._field_mapping.get(domain_field, domain_field)
        column: OrderableColumn | None = getattr(self._model, column_name, None)

        if column is None:
            raise ValueError(
                f"Field '{domain_field}' (mapped to '{column_name}') "
                f"not found on {self._model.__name__}"
            )

        return column

    def _apply_sorting(self, query: Select, sorting: list[SortingParam]) -> Select:
        clauses = [
            (
                self._resolve_column(p.field_name).asc()
                if p.sorting_order == SortingOrder.ASCENDING
                else self._resolve_column(p.field_name).desc()
            )
            for p in sorting
        ]
        return query.order_by(*clauses) if clauses else query

    def _apply_pagination(self, query: Select, pagination: Pagination) -> Select:

        applier = SQLAlchemyPaginationApplier(query, self._resolve_column)
        return pagination.accept(applier)

    def apply(
        self, query: Select, search: SearchQuery, model: type[DeclarativeBase]
    ) -> Select:
        self._model = model
        query = self._apply_sorting(query, search.sorting)
        query = self._apply_pagination(query, search.pagination)
        return query
