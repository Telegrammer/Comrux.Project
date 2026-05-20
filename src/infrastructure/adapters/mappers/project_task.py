from functools import singledispatchmethod

from application.models import ProjectTaskDetailsRead, ProjectTaskGroupAssigneeRead
from domain.value_objects import Name
from domain.entities import (
    ProjectGroupId,
    ProjectId,
    ProjectTask,
    ProjectTaskAssignee,
    ProjectTaskGroupAssignee,
    ProjectTaskId,
    ProjectTaskRoleAssignee,
    ProjectTaskUserAssignee,
    UserId,
)
from domain.enums import ProjectRole
from application.ports.mappers.errors import MappingError
from infrastructure.models import (
    ProjectTask as OrmProjectTask,
    ProjectTaskAssignee as OrmProjectTaskAssignee,
    RoleResponsible as OrmRoleResponsible,
    GroupResponsible as OrmGroupResponsible,
    UserResponsible as OrmUserResponsible,
)
from infrastructure.adapters.responsible_collector import SqlAlchemyResponsibleCollector


class SqlAlchemyProjectTaskMapper:
    def __init__(self):
        self._role_assignees: set[ProjectRole] = set()
        self._user_names: dict[UserId, Name] = {}
        self._group_assignees: dict[ProjectGroupId, ProjectTaskGroupAssigneeRead] = {}

    @singledispatchmethod
    def _responsible_to_domain(self, orm_responsible: ProjectTaskAssignee):
        raise MappingError(f"Unknown responsible type: {type(orm_responsible)}")

    @_responsible_to_domain.register
    def _(self, orm_responsible: OrmUserResponsible) -> ProjectTaskUserAssignee:

        value: str = str(orm_responsible.user_id)
        self._user_names[UserId(value)] = Name(orm_responsible.user.name)
        return ProjectTaskUserAssignee(value)

    @_responsible_to_domain.register
    def _(self, orm_responsible: OrmRoleResponsible) -> ProjectTaskRoleAssignee:
        self._role_assignees.add(orm_responsible.role)
        return ProjectTaskRoleAssignee(role=orm_responsible.role)

    @_responsible_to_domain.register
    def _(self, orm_responsible: OrmGroupResponsible) -> ProjectTaskGroupAssignee:
        gid = ProjectGroupId(str(orm_responsible.group_id))
        group_name = (
            Name(orm_responsible.group.name)
            if orm_responsible.group is not None
            else Name(".")
        )
        group_color = (
            orm_responsible.group.color
            if orm_responsible.group is not None
            else ""
        )
        self._group_assignees[gid] = ProjectTaskGroupAssigneeRead(
            name=group_name,
            color=group_color,
        )
        return ProjectTaskGroupAssignee(gid)

    def _to_domain_assignee(self, dto: OrmProjectTaskAssignee) -> ProjectTaskAssignee:
        return self._responsible_to_domain(dto.responsible)

    def to_dto(
        self,
        entity: ProjectTask,
        collector: SqlAlchemyResponsibleCollector,
    ) -> OrmProjectTask:
        return OrmProjectTask(
            id_=entity.id_,
            project_id=entity.project_id.value,
            creator_id=entity.creator_id.value,
            title=entity.title,
            description=entity.description,
            status=entity.status,
            start_at=entity.start_at,
            end_at=entity.end_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            assignees=[
                OrmProjectTaskAssignee(responsible_id=collector.resolve(assignee))
                for assignee in entity.assignees
            ],
        )

    def to_domain(self, dto: OrmProjectTask) -> ProjectTask:
        self._role_assignees = set()
        self._user_names = {}
        self._group_assignees = {}
        return ProjectTask(
            id_=ProjectTaskId(str(dto.id_)),
            project_id=ProjectId(str(dto.project_id)),
            title=dto.title,
            description=dto.description,
            status=dto.status,
            creator_id=UserId(str(dto.creator_id)),
            start_at=dto.start_at,
            end_at=dto.end_at,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            assignees=[self._to_domain_assignee(a) for a in dto.assignees],
        )

    def to_details_model(self, dto: OrmProjectTask) -> ProjectTaskDetailsRead:
        task = self.to_domain(dto)
        return ProjectTaskDetailsRead(
            task=task,
            role_assignees=self._role_assignees,
            user_assignees=self._user_names,
            group_assignees=self._group_assignees,
        )
