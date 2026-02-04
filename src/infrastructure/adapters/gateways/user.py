__all__ = ["SqlAlchemyUserCommandGateway", "SqlAlchemyUserQueryGateway"]


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import InterfaceError
from domain import User, UserId

from application.exceptions import UserAlreadyExistsError, UserNotFoundError
from application.ports.gateways.errors import GatewayFailedError
from infrastructure.adapters.mappers import SqlAlchemyUserMapper
from infrastructure.models import User as OrmUser
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