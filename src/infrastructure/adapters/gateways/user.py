__all__ = ["SqlAlchemyUserCommandGateway", "SqlAlchemyUserQueryGateway"]


from typing import Iterable, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import InterfaceError
from domain import User, UserId

from application.exceptions import UserAlreadyExistsError, UserNotFoundError
from application.ports import UserListParams
from application.ports.gateways.errors import GatewayFailedError
from infrastructure.adapters.mappers import SqlAlchemyUserMapper
from infrastructure.models import User as OrmUser, SqlAlchemySearchParams
from infrastructure.exceptions.common import create_error_aware_decorator
from infrastructure.exceptions.asyncpg_unique_error_handler import (
    unique_violation_aware,
)


network_error_aware = create_error_aware_decorator(
    {
        frozenset(
            {ConnectionRefusedError, ConnectionResetError, InterfaceError}
        ): GatewayFailedError
    }
)

from application.ports.gateways.errors import GatewayFailedError


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

    def __init__(self, session: AsyncSession, mapper: SqlAlchemyUserMapper):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyUserMapper = mapper

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
        self, ids: Iterable[UserId], search_params: UserListParams
    ) -> Sequence[User]:

        search: SqlAlchemySearchParams = self._mapper.generate_search_params(
            search_params, OrmUser
        )
        stmt = (
            select(OrmUser)
            .where(OrmUser.id_.in_(ids))
            .order_by(*search.orders)
            .slice(
                search_params.pagination.offset,
                search_params.pagination.offset + search_params.pagination.limit,
            )
        )

        response = await self._session.scalars(stmt)
        users: Sequence[User] = response.all()
        return [self._mapper.to_domain(user) for user in users]
