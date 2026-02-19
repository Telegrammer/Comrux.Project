__all__ = ["ApplicationProvider"]


from dishka import Provider, provide, Scope, from_context
from functools import partial
from typing import Callable
from setup.config import Settings

from domain import User, UserId
from domain.value_objects import Name, BirthDate
from dateutil.relativedelta import relativedelta

from application.compositions import (
    CreateProjectComposition,
    UpdateProjectComposition,
    DeleteProjectComposition,
    CreateUserComposition,
    AddProjectMemberComposition,
    ListProjectMembersComposition,
    RemoveProjectMemberComposition,
    ListCurrentUserProjectsComposition,
    GrantOwnerComposition,
    SetMemberRoleComposition,
    CreateDirectoryComposition,
    CreateDocumentComposition,
    ListDirectoryContentCompostion,
    ListProjectsComposition,
    DeleteDocumentComposition,
    DeleteDirectoryComposition,
    CreateContentTicketComposition,
)
from application.usecases import (
    CreateProjectUsecase,
    ListProjectsUsecase,
    UpdateProjectUsecase,
    DeleteProjectUsecase,
    CreateUserUsecase,
    AddProjectMemberUsecase,
    ListProjectMembersUsecase,
    RemoveProjectMemberUsecase,
    ListCurrentUserProjectsUsecase,
    GrantOwnerUsecase,
    SetMemberRoleUsecase,
    CreateDirectoryUsecase,
    CreateDocumentUsecase,
    ListDirectoryContentUsecase,
    DeleteDocumentUsecase,
    DeleteDirectoryUsecase,
    CreateContentTicketUsecase,
)
from application.services import (
    CurrentUserService,
    ProjectUnitCreationContextService,
    DocumentManageContextService,
)
from application.ports import Clock, TaskNotifier
from application.ports.mappers import (
    ProjectMapper,
    UserMapper,
    DirectoryMapper,
    TaskMapper,
)
from application.ports.gateways import (
    ProjectCommandGateway,
    ProjectQueryGateway,
    UserCommandGateway,
    UserQueryGateway,
    DirectoryCommandGateway,
    DirectoryQueryGateway,
    DocumentCommandGateway,
    DocumentQueryGateway,
    ProjectUnitQueryGateway,
    TaskCommandGateway,
)
from infrastructure.adapters import (
    TimestampClock,
    JsonProjectUnitVisitor,
    KafkaTaskNotifier,
)
from infrastructure.adapters.mappers import (
    SqlAlchemyProjectMapper,
    SqlAlchemyUserMapper,
    SqlAlchemyDirectoryMapper,
    SqlAlchemyDocumentMapper,
    SqlAlchemyTaskMapper,
    ProjectUnitNodeMapper,
)
from infrastructure.adapters.gateways import (
    SqlAlchemyProjectCommandGateway,
    SqlAlchemyProjectQueryGateway,
    SqlAlchemyUserCommandGateway,
    SqlAlchemyUserQueryGateway,
    SqlAlchemyDirectoryCommandGateway,
    SqlAlchemyDirectoryQueryGateway,
    SqlAlchemyDocumentCommandGateway,
    SqlAlchemyDocumentQueryGateway,
    SQLAlchemyQueryBuilder,
    SqlAclhemyProjectUnitQueryGateway,
    SqlAlchemyTaskCommandGateway,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST
    settings = from_context(Settings, scope=Scope.APP)
    user_id = from_context(UserId)

    clock = provide(source=TimestampClock, provides=Clock)

    @provide
    def provide_query_builder(self) -> SQLAlchemyQueryBuilder:
        return SQLAlchemyQueryBuilder()

    task_mapper = provide(source=SqlAlchemyTaskMapper, provides=TaskMapper)
    task_gateway = provide(
        source=SqlAlchemyTaskCommandGateway, provides=TaskCommandGateway
    )
    task_notifier = provide(source=KafkaTaskNotifier, provides=TaskNotifier)

    user_mapper = provide(SqlAlchemyUserMapper)
    user_command_gateway = provide(
        source=SqlAlchemyUserCommandGateway, provides=UserCommandGateway
    )
    user_query_gateway = provide(
        source=SqlAlchemyUserQueryGateway, provides=UserQueryGateway
    )
    create_user_usecase = provide(CreateUserUsecase)
    create_user_composition = provide(CreateUserComposition)

    @provide
    def provide_current_user_service(
        self, user_id: UserId, user_gateway: UserQueryGateway
    ) -> CurrentUserService:
        return CurrentUserService(user_id=user_id, gateway=user_gateway)

    document_manage_serivce = provide(DocumentManageContextService)
    project_unit_creation_service = provide(ProjectUnitCreationContextService)

    project_mapper = provide(SqlAlchemyProjectMapper)

    project_command_gateway = provide(
        source=SqlAlchemyProjectCommandGateway, provides=ProjectCommandGateway
    )

    project_query_gateway = provide(
        source=SqlAlchemyProjectQueryGateway,
        provides=ProjectQueryGateway,
    )

    project_unit_gateway = provide(
        source=SqlAclhemyProjectUnitQueryGateway, provides=ProjectUnitQueryGateway
    )
    project_unit_mapper = provide(ProjectUnitNodeMapper)

    @provide
    def provide_dir_mapper(self, clock: Clock) -> SqlAlchemyDirectoryMapper:
        return SqlAlchemyDirectoryMapper(
            clock=clock, unit_visitor=JsonProjectUnitVisitor()
        )

    @provide
    def provide_doc_mapper(self, clock: Clock) -> SqlAlchemyDocumentMapper:
        return SqlAlchemyDocumentMapper(
            clock=clock, unit_visitor=JsonProjectUnitVisitor()
        )

    directory_command_gateway = provide(
        source=SqlAlchemyDirectoryCommandGateway, provides=DirectoryCommandGateway
    )
    directory_query_gateway = provide(
        source=SqlAlchemyDirectoryQueryGateway, provides=DirectoryQueryGateway
    )
    document_command_gateway = provide(
        source=SqlAlchemyDocumentCommandGateway, provides=DocumentCommandGateway
    )
    document_query_gateway = provide(
        source=SqlAlchemyDocumentQueryGateway, provides=DocumentQueryGateway
    )

    create_project_usecase = provide(CreateProjectUsecase)
    create_project_composition = provide(CreateProjectComposition)
    list_projects_usecase = provide(ListProjectsUsecase)
    update_project_usecase = provide(UpdateProjectUsecase)
    update_project_composition = provide(UpdateProjectComposition)
    delete_project_usecase = provide(DeleteProjectUsecase)
    delete_project_composition = provide(DeleteProjectComposition)
    add_member_usecase = provide(AddProjectMemberUsecase)
    add_member_composition = provide(AddProjectMemberComposition)
    list_project_members_usecase = provide(ListProjectMembersUsecase)
    list_project_members_compostion = provide(ListProjectMembersComposition)
    remove_member_usecase = provide(RemoveProjectMemberUsecase)
    remover_member_composition = provide(RemoveProjectMemberComposition)
    list_current_user_projects_usecase = provide(ListCurrentUserProjectsUsecase)
    list_current_user_projects_composition = provide(ListCurrentUserProjectsComposition)
    grant_owner_usecase = provide(GrantOwnerUsecase)
    grant_owner_comosition = provide(GrantOwnerComposition)
    set_role_usecase = provide(SetMemberRoleUsecase)
    set_role_composition = provide(SetMemberRoleComposition)
    create_directory_usecase = provide(CreateDirectoryUsecase)
    create_directory_composition = provide(CreateDirectoryComposition)
    create_document_usecase = provide(CreateDocumentUsecase)
    create_document_composition = provide(CreateDocumentComposition)
    list_dir_content_usecase = provide(ListDirectoryContentUsecase)
    list_dir_content_composition = provide(ListDirectoryContentCompostion)
    list_projects_composition = provide(ListProjectsComposition)
    delete_document_usecase = provide(DeleteDocumentUsecase)
    delete_document_composition = provide(DeleteDocumentComposition)
    delete_directory_usecase = provide(DeleteDirectoryUsecase)
    delete_directory_composition = provide(DeleteDirectoryComposition)
    create_ticket_usecase = provide(CreateContentTicketUsecase)
    create_ticket_composition = provide(CreateContentTicketComposition)
