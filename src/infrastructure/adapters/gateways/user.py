__all__ = ["SqlAlchemyUserCommandGateway", "SqlAlchemyUserQueryGateway"]


from typing import Iterable, Sequence
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from domain import User, UserId

from application.exceptions import UserAlreadyExistsError, UserNotFoundError
from application.ports import UserListParams
from infrastructure.adapters.mappers import SqlAlchemyUserMapper
from infrastructure.models import User as OrmUser
from infrastructure.exceptions.error_aware_decorators import network_error_aware
from infrastructure.exceptions.asyncpg_unique_error_handler import (
    unique_violation_aware,
)
from .query_builder import SQLAlchemyQueryBuilder


class SqlAlchemyUserCommandGateway:

    def __init__(self, session: AsyncSession, mapper: SqlAlchemyUserMapper):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyUserMapper = mapper

    @network_error_aware("Cannot add user: users are not reachable")
    @unique_violation_aware(
        UserAlreadyExistsError("User with the same data already exists")
    )
    async def add(self, user: User):
        orm_user: OrmUser = self._mapper.to_dto(user)
        self._session.add(orm_user)
        await self._session.flush()


class SqlAlchemyUserQueryGateway:

    def __init__(
        self,
        session: AsyncSession,
        mapper: SqlAlchemyUserMapper,
        query_builder: SQLAlchemyQueryBuilder,
    ):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyUserMapper = mapper
        self._query_builder: SQLAlchemyQueryBuilder = query_builder

    @network_error_aware("Cannot find user: can't reach to them")
    async def by_id(self, user_id: UserId) -> User:
        stmt = select(OrmUser).where(OrmUser.id_ == user_id)
        response = await self._session.execute(stmt)
        user = response.scalar_one_or_none()

        if not user:
            raise UserNotFoundError("User with given id does not exist")
        return self._mapper.to_domain(user)

    @network_error_aware("Cannot find users: can't reach to them")
    async def by_ids(
        self, ids: Iterable[UserId], search_params: UserListParams | None = None
    ) -> Sequence[User]:

        stmt: Select = select(OrmUser).where(OrmUser.id_.in_(ids))
        if search_params:
            stmt = self._query_builder.apply(stmt, search_params, OrmUser)

        response = await self._session.scalars(stmt)
        users: Sequence[OrmUser] = response.all()
        return [self._mapper.to_domain(user) for user in users]

    @network_error_aware("Cannot find users: can't reach to them")
    async def read_all(self, params: UserListParams) -> Sequence[User]:
        stmt: Select = select(OrmUser)
        stmt = self._query_builder.apply(stmt, params, OrmUser)
        response = await self._session.scalars(stmt)
        users: Sequence[OrmUser] = response.all()
        return [self._mapper.to_domain(user) for user in users]
