from typing import Protocol, Callable
from sqlalchemy import BinaryExpression, UnaryExpression


class OrderableColumn(Protocol):

    def asc(self) -> UnaryExpression[bool]: ...
    def desc(self) -> UnaryExpression[bool]: ...
    def __gt__(self, other: object) -> BinaryExpression[bool]: ...


type ColumnResolver = Callable[[str], OrderableColumn]
