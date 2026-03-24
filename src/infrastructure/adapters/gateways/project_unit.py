from typing import Sequence
from sqlalchemy import select, Select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from domain import DirectoryId, ProjectUnit


from application.ports.gateways import ProjectUnitListParams

from infrastructure.adapters.mappers import ProjectUnitNodeMapper
from infrastructure.models import ProjectUnitNode
from .query_builder import SQLAlchemyQueryBuilder


class SqlAclhemyProjectUnitCommandGateway:

    def __init__(self, mapper: ProjectUnitNodeMapper, session: AsyncSession):
        self._mapper = mapper
        self._session = session

    async def update(self, unit: ProjectUnit) -> None:
        stmt = (
            sql_update(ProjectUnitNode)
            .where(ProjectUnitNode.id_ == unit.id_)
            .values(
                name=unit.name.value,
                access_list_id=unit.access_list,
                created_by=unit.created_by.value,
            )
        )
        await self._session.execute(stmt)


class SqlAclhemyProjectUnitQueryGateway:

    def __init__(
        self,
        mapper: ProjectUnitNodeMapper,
        session: AsyncSession,
        query_builder: SQLAlchemyQueryBuilder,
    ):
        self._session: AsyncSession = session
        self._mapper: ProjectUnitNodeMapper = mapper
        self._query_builder: SQLAlchemyQueryBuilder = query_builder

    async def by_directory(
        self, directory_id: DirectoryId, params: ProjectUnitListParams
    ) -> Sequence[ProjectUnit]:
        stmt: Select = select(ProjectUnitNode).where(
            ProjectUnitNode.parent_id == directory_id
        )

        stmt = self._query_builder.apply(stmt, params, ProjectUnitNode).order_by(
            ProjectUnitNode.unit_type
        )
        nodes: Sequence[ProjectUnitNode] = (await self._session.scalars(stmt)).all()

        return [self._mapper.to_domain(node) for node in nodes]
