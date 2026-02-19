__all__ = ["SqlAlchemyTaskCommandGateway", "SqlAlchemyTaskQueryGateway"]


from typing import Sequence
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


from domain.entities import Task, TaskId
from domain.enums import TaskStatus

from application.ports.gateways.query_params import TaskListParams
from application.ports.mappers import TaskMapper
from application.exceptions import TaskAlreadyExistsError
from infrastructure.models import Task as OrmTask
from infrastructure.exceptions.error_aware_decorators import network_error_aware
from infrastructure.exceptions.asyncpg_unique_error_handler import (
    unique_violation_aware,
)


class SqlAlchemyTaskCommandGateway:

    def __init__(self, session: AsyncSession, mapper: TaskMapper):
        self._session: AsyncSession = session
        self._mapper: TaskMapper = mapper

    @unique_violation_aware(
        TaskAlreadyExistsError("User with same data already exists")
    )
    @network_error_aware("Cannot add task")
    async def add(self, task: Task):
        orm_task: OrmTask = self._mapper.to_dto(task)
        self._session.add(orm_task)
        await self._session.flush()

    @network_error_aware("Cannot claim tasks: they are unreachable")
    async def claim_created_tasks(self, filters: TaskListParams) -> Sequence[Task]:

        subq = (
            select(OrmTask.id_)
            .where(OrmTask.status == TaskStatus.CREATED)
            .where(OrmTask.resend_time < filters.current_resend_time)
            .limit(filters.batch_size)
            .with_for_update(skip_locked=True)
            .scalar_subquery()
        )

        stmt = (
            update(OrmTask)
            .where(OrmTask.id_.in_(subq))
            .values(status=TaskStatus.PROCESSING)
            .returning(OrmTask)
        )
        response = await self._session.execute(stmt)
        tasks: Sequence[Task] = response.scalars().all()

        return [self._mapper.to_domain(task) for task in tasks]

    @network_error_aware("Cannot add task")
    async def mark_sent(self, task_id: TaskId) -> None:

        stmt = (
            update(OrmTask)
            .where(OrmTask.id_ == task_id)
            .values(attempts=OrmTask.attempts + 1, status=TaskStatus.SENT)
        )
        await self._session.execute(stmt)

    @network_error_aware("Cannot update task")
    async def update(self, task: Task) -> None:
        orm_task: Task = self._mapper.to_dto(task)
        await self._session.merge(orm_task)


class SqlAlchemyTaskQueryGateway:

    def __init__(self, session: AsyncSession, mapper: TaskMapper):
        self._session: AsyncSession = session
        self._mapper: TaskMapper = mapper
