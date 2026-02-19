from domain.entities import Task, TaskId
from domain.value_objects import FutureDatetime, PassedDatetime

from application.ports.mappers import TaskMapper
from infrastructure.models import Task as OrmTask


class SqlAlchemyTaskMapper(TaskMapper[OrmTask]):

    def to_dto(self, entity: Task, old_dto: OrmTask | None = None) -> OrmTask:

        return OrmTask(
            id_=entity.id_,
            task_type=entity.task_type,
            status=entity.status,
            payload=entity.payload,
            created_at=entity.created_at,
            resend_time=entity.resend_time,
            attempts=entity.attempts,
        )

    def to_domain(self, dto: OrmTask) -> Task:
        return Task(
            id_=TaskId(dto.id_.__str__()),
            task_type=dto.task_type,
            status=dto.status,
            payload=dto.payload,
            created_at=PassedDatetime(dto.created_at, dto.created_at),
            resend_time=FutureDatetime(dto.resend_time, dto.created_at),
            attempts=dto.attempts,
        )
