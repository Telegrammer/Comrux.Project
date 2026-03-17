from application.ports.gateways.query_params import (
    EqFilter,
    RangeFilter,
    OrFilter,
    LikeFilter,
    FilterVisitor,
)

from sqlalchemy import Select, ColumnElement, or_
from .base import ColumnResolver, OrderableColumn


class SqlAlchemyFilterVisitor(FilterVisitor[ColumnElement[bool]]):
    def __init__(self, column_resolver: ColumnResolver):
        self._column_resolver = column_resolver

    def _make_contains_pattern(
        self, value: str, escape_char: str = "\\"
    ) -> tuple[str, str]:
        escaped = (
            value.replace(escape_char, escape_char * 2)
            .replace("%", escape_char + "%")
            .replace("_", escape_char + "_")
        )
        return f"%{escaped}%", escape_char

    def visit_eq(self, param: EqFilter) -> ColumnElement[bool]:
        column: OrderableColumn = self._column_resolver(param.field_name)
        return column == param.value

    def visit_like(self, param: LikeFilter) -> ColumnElement[bool]:
        column: OrderableColumn = self._column_resolver(param.field_name)
        pattern, escape_char = self._make_contains_pattern(param.value)
        return column.ilike(pattern, escape=escape_char)

    def visit_or(self, param: OrFilter) -> ColumnElement[bool]:
        conditions = [f.accept(self) for f in param.filters]
        return or_(*conditions)
