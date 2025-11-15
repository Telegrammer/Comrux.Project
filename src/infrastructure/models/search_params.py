__all__ = ["SqlAlchemySearchParams"]


from dataclasses import dataclass
from sqlalchemy import UnaryExpression

@dataclass
class SqlAlchemySearchParams:
    orders: list[UnaryExpression]
    # TODO SEARCH FILTER PAGINATE (add all search params)
