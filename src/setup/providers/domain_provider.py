__all__ = ["DomainProvider"]


from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from dishka import Provider, provide, Scope, from_context
from setup.config import Settings


from domain import (
    ProjectService,
    UserService,
    DirectoryService,
    DocumentService,
    ProjectGroupService,
    ProjectTaskDomainService,
)
from domain.services import ContentTicketService, TaskService, AccessListService
from domain.export import ProjectReleaseService
from domain.export.ports import ProjectReleaseIdGenerator
from domain.policies import BirthDatePolicy, ContentTicketValidityPolicy, TaskPolicy
from domain.ports.access_rule_responsible_resolution_order import (
    FixedAccessRuleResponsibleResolutionOrder,
)
from domain.ports import (
    ProjectIdGenerator,
    UserIdGenerator,
    ProjectUnitIdGenerator,
    ProjectUnitVisitor,
    ContentIdGenerator,
    TaskIdGenerator,
    AccessListIdGenerator,
    ProjectGroupIdGenerator,
    ProjectTaskIdGenerator,
    AccessRuleResponsibleResolutionOrder,
)
from infrastructure.adapters import (
    Uuid4ProjectIdGenerator,
    Uuid4UserIdGenerator,
    Uuid4ProjectUnitIdGenerator,
    Uuid4ContentIdGenerator,
    Uuid4AccessListIdGenerator,
    Uuid4ProjectGroupIdGenerator,
    Uuid4ProjectTaskIdGenerator,
    TaskUuid4Generator,
    JsonProjectUnitVisitor,
)
from infrastructure.export import Uuid4ProjectReleaseIdGenerator


class DomainProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    project_id_generator = provide(
        source=Uuid4ProjectIdGenerator, provides=ProjectIdGenerator
    )
    project_service = provide(ProjectService)
    user_id_generator = provide(source=Uuid4UserIdGenerator, provides=UserIdGenerator)
    project_unit_id_generator = provide(
        source=Uuid4ProjectUnitIdGenerator, provides=ProjectUnitIdGenerator
    )
    content_id_generator = provide(
        source=Uuid4ContentIdGenerator, provides=ContentIdGenerator
    )
    task_id_generator = provide(source=TaskUuid4Generator, provides=TaskIdGenerator)
    project_release_id_generator = provide(
        source=Uuid4ProjectReleaseIdGenerator,
        provides=ProjectReleaseIdGenerator,
    )
    project_unit_visitor = provide(
        source=JsonProjectUnitVisitor, provides=ProjectUnitVisitor
    )

    access_list_id_generator = provide(
        source=Uuid4AccessListIdGenerator, provides=AccessListIdGenerator
    )
    project_group_id_generator = provide(
        source=Uuid4ProjectGroupIdGenerator, provides=ProjectGroupIdGenerator
    )
    project_task_id_generator = provide(
        source=Uuid4ProjectTaskIdGenerator, provides=ProjectTaskIdGenerator
    )

    @provide
    def provide_access_rule_responsible_resolution_order(
        self,
    ) -> AccessRuleResponsibleResolutionOrder:
        return FixedAccessRuleResponsibleResolutionOrder()

    @provide
    def provide_birthdate_policy(self) -> BirthDatePolicy:
        return BirthDatePolicy(date(1900, 1, 1), relativedelta(years=12))

    @provide
    def provide_content_policy(self) -> ContentTicketValidityPolicy:
        return ContentTicketValidityPolicy(ttl=timedelta(seconds=6000))

    @provide
    def provide_task_policy(self) -> TaskPolicy:
        return TaskPolicy(
            init_resend_delta=timedelta(seconds=10),
            backoff_value=0.1,
            max_attempt_count=3,
        )

    user_service = provide(UserService)
    directory_service = provide(DirectoryService)
    document_service = provide(DocumentService)
    ticket_service = provide(ContentTicketService)
    task_service = provide(TaskService)
    project_release_service = provide(ProjectReleaseService)
    acl_service = provide(AccessListService)
    project_group_service = provide(ProjectGroupService)
    project_task_domain_service = provide(ProjectTaskDomainService)