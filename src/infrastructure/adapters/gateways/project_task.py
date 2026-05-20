from datetime import datetime
from typing import Sequence

from sqlalchemy import String, and_, bindparam, cast, exists, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.models import ProjectTaskDetailsRead
from application.exceptions import (
    ProjectTaskAlreadyExistsError,
    ProjectTaskNotFoundError,
)
from application.ports.gateways.query_params import ProjectTaskListParams
from domain.entities import ProjectId, ProjectTask, ProjectTaskId
from domain.enums import ProjectTaskStatus
from infrastructure.adapters.responsible_collector import SqlAlchemyResponsibleCollector
from infrastructure.adapters.mappers import SqlAlchemyProjectTaskMapper
from infrastructure.exceptions import network_error_aware, unique_violation_aware
from infrastructure.models import (
    ProjectGroup as OrmProjectGroup,
    ProjectGroupParticipant as OrmProjectGroupParticipant,
    ProjectMembership as OrmProjectMembership,
    ProjectTask as OrmProjectTask,
    ProjectTaskAssignee as OrmProjectTaskAssignee,
    GroupResponsible as OrmGroupResponsible,
    RoleResponsible as OrmRoleResponsible,
    User as OrmUser,
    UserResponsible as OrmUserResponsible,
)

from .query_builder import SQLAlchemyQueryBuilder


class SqlAlchemyProjectTaskCommandGateway:
    def __init__(
        self, session: AsyncSession, mapper: SqlAlchemyProjectTaskMapper
    ) -> None:
        self._session = session
        self._mapper = mapper

    @unique_violation_aware(
        ProjectTaskAlreadyExistsError("Project task already exists with same identity")
    )
    @network_error_aware("Cannot add task: tasks are unavailable")
    async def add(self, task: ProjectTask) -> None:
        collector = SqlAlchemyResponsibleCollector()
        for assignee in task.assignees:
            collector.collect(assignee)
        await collector.persist_responsibles(self._session)
        self._session.add(self._mapper.to_dto(task, collector))
        await self._session.flush()

    @network_error_aware("Cannot update task: tasks are unavailable")
    async def update(self, task: ProjectTask) -> None:
        stmt = (
            update(OrmProjectTask)
            .where(OrmProjectTask.id_ == task.id_)
            .values(
                title=task.title,
                description=task.description,
                status=task.status,
                start_at=task.start_at,
                end_at=task.end_at,
                updated_at=task.updated_at,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

    @network_error_aware("Cannot update tasks: tasks are unavailable")
    async def update_many(self, tasks: Sequence[ProjectTask]) -> None:
        if not tasks:
            return

        stmt = (
            update(OrmProjectTask)
            .where(OrmProjectTask.id_ == bindparam("id_"))
            .values(
                title=bindparam("title"),
                description=bindparam("description"),
                status=bindparam("status"),
                start_at=bindparam("start_at"),
                end_at=bindparam("end_at"),
                updated_at=bindparam("updated_at"),
            )
        )
        payload = [
            {
                "id_": task.id_,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "start_at": task.start_at,
                "end_at": task.end_at,
                "updated_at": task.updated_at,
            }
            for task in tasks
        ]
        await self._session.execute(stmt, payload)
        await self._session.flush()

    @network_error_aware("Cannot sync overdue tasks: tasks are unavailable")
    async def sync_overdue_batch(self, project_id: ProjectId, now: datetime) -> int:
        stmt = (
            update(OrmProjectTask)
            .where(OrmProjectTask.project_id == project_id)
            .where(OrmProjectTask.end_at < now)
            .where(
                OrmProjectTask.status.not_in(
                    [ProjectTaskStatus.DONE, ProjectTaskStatus.CANCELED]
                )
            )
            .values(status=ProjectTaskStatus.OVERDUE, updated_at=now)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return int(result.rowcount or 0)


class SqlAlchemyProjectTaskQueryGateway:
    def __init__(
        self,
        session: AsyncSession,
        mapper: SqlAlchemyProjectTaskMapper,
        query_builder: SQLAlchemyQueryBuilder,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._query_builder = query_builder

    @staticmethod
    def _assignee_loading_options():
        return (
            selectinload(OrmProjectTask.assignees)
            .selectinload(OrmProjectTaskAssignee.responsible)
            .selectin_polymorphic(
                [OrmUserResponsible, OrmRoleResponsible, OrmGroupResponsible]
            ),
        )

    @network_error_aware("Cannot list tasks: tasks are unavailable")
    async def by_project(
        self, project_id: ProjectId, params: ProjectTaskListParams
    ) -> Sequence[ProjectTask]:
        stmt = (
            select(OrmProjectTask)
            .where(OrmProjectTask.project_id == project_id)
            .options(*self._assignee_loading_options())
        )
        if params.assigned_to_user_id is not None:
            uid = params.assigned_to_user_id
            uid_value = uid.value if hasattr(uid, "value") else uid
            mine_via_user = exists(
                select(1)
                .select_from(OrmProjectTaskAssignee)
                .join(
                    OrmUserResponsible,
                    OrmUserResponsible.id_ == OrmProjectTaskAssignee.responsible_id,
                )
                .where(
                    OrmProjectTaskAssignee.task_id == OrmProjectTask.id_,
                    OrmUserResponsible.user_id == uid_value,
                )
            )
            mine_via_group = exists(
                select(1)
                .select_from(OrmProjectTaskAssignee)
                .join(
                    OrmGroupResponsible,
                    OrmGroupResponsible.id_ == OrmProjectTaskAssignee.responsible_id,
                )
                .join(
                    OrmProjectGroupParticipant,
                    OrmProjectGroupParticipant.group_id == OrmGroupResponsible.group_id,
                )
                .where(
                    OrmProjectTaskAssignee.task_id == OrmProjectTask.id_,
                    OrmProjectGroupParticipant.user_id == uid_value,
                )
            )
            mine_via_role = exists(
                select(1)
                .select_from(OrmProjectTaskAssignee)
                .join(
                    OrmRoleResponsible,
                    OrmRoleResponsible.id_ == OrmProjectTaskAssignee.responsible_id,
                )
                .join(
                    OrmProjectMembership,
                    and_(
                        OrmProjectMembership.project_id == project_id,
                        OrmProjectMembership.user_id == uid_value,
                        cast(OrmProjectMembership.role, String)
                        == cast(OrmRoleResponsible.role, String),
                    ),
                )
                .where(OrmProjectTaskAssignee.task_id == OrmProjectTask.id_)
            )
            stmt = stmt.where(
                or_(mine_via_user, mine_via_group, mine_via_role)
            )
        stmt = self._query_builder.apply(stmt, params, OrmProjectTask)
        response = (await self._session.execute(stmt)).unique().scalars().all()
        return [self._mapper.to_domain(item) for item in response]

    @network_error_aware("Cannot find task: tasks are unavailable")
    async def by_id(self, task_id: ProjectTaskId) -> ProjectTask:
        stmt = (
            select(OrmProjectTask)
            .where(OrmProjectTask.id_ == task_id)
            .options(*self._assignee_loading_options())
        )
        dto = (await self._session.execute(stmt)).scalar_one_or_none()
        if dto is None:
            raise ProjectTaskNotFoundError("Task with given id does not exist")
        return self._mapper.to_domain(dto)

    @network_error_aware("Cannot find task: tasks are unavailable")
    async def by_id_detailed(self, task_id: ProjectTaskId) -> ProjectTaskDetailsRead:
        stmt = (
            select(OrmProjectTask)
            .where(OrmProjectTask.id_ == task_id)
            .options(
                *self._assignee_loading_options(),
                selectinload(OrmProjectTask.assignees)
                .selectinload(OrmProjectTaskAssignee.responsible.of_type(OrmUserResponsible))
                .joinedload(OrmUserResponsible.user)
                .load_only(OrmUser.name),
                selectinload(OrmProjectTask.assignees)
                .selectinload(
                    OrmProjectTaskAssignee.responsible.of_type(OrmGroupResponsible)
                )
                .joinedload(OrmGroupResponsible.group)
                .load_only(OrmProjectGroup.name, OrmProjectGroup.color),
            )
        )
        dto = (await self._session.execute(stmt)).scalar_one_or_none()
        if dto is None:
            raise ProjectTaskNotFoundError("Task with given id does not exist")
        return self._mapper.to_details_model(dto)
