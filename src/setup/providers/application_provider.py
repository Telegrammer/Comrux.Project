__all__ = ["ApplicationProvider"]


from dishka import Provider, provide, Scope, from_context
from setup.config import Settings

from domain import UserId

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
    GetUserCompostion,
    ListUsersComposition,
    CreateAccessListComposition,
    ListProjectAccessListsComposition,
    DeleteAccessListComposition,
    AssignAccessListComposition,
    SetProjectAccessComposition,
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
    GetDocumentContentUsecase,
    GetUserUsecase,
    ListUsersUsecase,
    GetCurrentUserUsecase,
    CreateAccessListUsecase,
    ListAccessListsUsecase,
    DeleteAccessListUsecase,
    AssignAccessListToDirectoryUsecase,
    AssignAccessListToDocumentUsecase,
    SetProjectAccessUsecase,
)
from application.services import (
    CurrentUserService,
    DirectoryManageContextService,
    DocumentManageContextService,
    DocumentReadContextService,
    ProjectUnitPermissionService,
    AssignAccessListService,
)
from application.ports import Clock, TaskNotifier
from application.ports.mappers import (
    TaskMapper,
)
from application.ports.gateways import (
    ContentQueryGateway,
    ProjectCommandGateway,
    ProjectQueryGateway,
    UserCommandGateway,
    UserQueryGateway,
    DirectoryCommandGateway,
    DirectoryQueryGateway,
    DocumentCommandGateway,
    DocumentQueryGateway,
    ProjectUnitCommandGateway,
    ProjectUnitQueryGateway,
    TaskCommandGateway,
    AccessListCommandGateway,
    AccessListQueryGateway,
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
    SqlAlchemyAccessListMapper,
)
from infrastructure.adapters.gateways import (
    HttpContentQueryGateway,
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
    SqlAlchemyAccessListCommandGateway,
    SqlAlchemyAccessListQueryGateway,
    SqlAclhemyProjectUnitCommandGateway,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST
    settings = from_context(Settings, scope=Scope.APP)
    user_id = from_context(UserId | None)

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
        self, user_id: UserId | None, user_gateway: UserQueryGateway
    ) -> CurrentUserService:
        return CurrentUserService(user_id=user_id, gateway=user_gateway)

    document_manage_serivce = provide(DocumentManageContextService)
    document_read_service = provide(DocumentReadContextService)
    directory_manage_serivce = provide(DirectoryManageContextService)
    project_unit_permission_service = provide(ProjectUnitPermissionService)
    access_list_assign_service = provide(AssignAccessListService)

    project_mapper = provide(SqlAlchemyProjectMapper)

    project_command_gateway = provide(
        source=SqlAlchemyProjectCommandGateway, provides=ProjectCommandGateway
    )

    project_query_gateway = provide(
        source=SqlAlchemyProjectQueryGateway,
        provides=ProjectQueryGateway,
    )

    project_unit_query_gateway = provide(
        source=SqlAclhemyProjectUnitQueryGateway, provides=ProjectUnitQueryGateway
    )
    project_unit_command_gateway = provide(
        source=SqlAclhemyProjectUnitCommandGateway, provides=ProjectUnitCommandGateway
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
    content_query_gateway = provide(
        source=HttpContentQueryGateway, provides=ContentQueryGateway
    )

    access_list_mapper = provide(SqlAlchemyAccessListMapper)
    access_list_command_gateway = provide(
        source=SqlAlchemyAccessListCommandGateway, provides=AccessListCommandGateway
    )
    access_list_query_gateway = provide(
        source=SqlAlchemyAccessListQueryGateway,
        provides=AccessListQueryGateway,
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
    get_document_content_usecase = provide(GetDocumentContentUsecase)
    create_ticket_composition = provide(CreateContentTicketComposition)
    get_user_usecase = provide(GetUserUsecase)
    get_user_composition = provide(GetUserCompostion)
    list_users_usecase = provide(ListUsersUsecase)
    list_users_composition = provide(ListUsersComposition)
    get_current_user = provide(GetCurrentUserUsecase)
    create_access_list_usecase = provide(CreateAccessListUsecase)
    create_access_list_composition = provide(CreateAccessListComposition)
    list_access_lists_usecase = provide(ListAccessListsUsecase)
    list_access_lists_composition = provide(ListProjectAccessListsComposition)
    delete_access_list_usecase = provide(DeleteAccessListUsecase)
    delete_access_list_composition = provide(DeleteAccessListComposition)
    assign_acl_dir_usecase = provide(AssignAccessListToDirectoryUsecase)
    assign_acl_doc_usecase = provide(AssignAccessListToDocumentUsecase)
    assign_acl_composition = provide(AssignAccessListComposition)
    set_project_privateness_usecase = provide(SetProjectAccessUsecase)
    set_project_access_composition = provide(SetProjectAccessComposition)
