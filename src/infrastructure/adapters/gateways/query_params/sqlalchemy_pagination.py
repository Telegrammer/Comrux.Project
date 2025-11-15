from dataclasses import dataclass
from sqlalchemy import Select, tuple_

from application.ports.gateways.query_params import (
    OffsetPagination,
    CreationPagination,
)


@dataclass
class SqlAclhemyOffestPagination(OffsetPagination):

    def accept(self, query: Select) -> Select:
        return query.slice(self.offset, self.limit)

