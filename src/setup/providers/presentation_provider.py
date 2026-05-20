__all__ = ["PresentationProvider"]


from dishka import Provider, provide, Scope, from_context
from setup.config import Settings

from application.compositions import ListDirectoryContentCompostion

from presentation.presenters import (
    OrdersPresenter,
    AuthInfoPresenter,
    JwtAuthInfoPresenter,
    ContentTicketPresenter,
    JwtContentTicketPresenter,
    PydanticProjectUnitVisitor,
    AccessListCreateRuleResponsiblePresenter,
    ProjectTaskAssigneePresenter,
)
from presentation.handlers import (
    CreateProjectHandler,
    ListProjectsHandler,
    UpdateProjectHandler,
    DeleteProjectHandler,
    CreateUserHandler,
    AddProjectMemberHandler,
    ListProjectMembersHandler,
    RemoveProjectMemberHandler,
    ListCurrentUserProjectsHandler,
    GrantOwnerHandler,
    SetMemberRoleHandler,
    CreateDirectoryHandler,
    CreateDocumentHandler,
    ListDirectoryContentHandler,
    DeleteDocumentHandler,
    DeleteDirectoryHandler,
    CreateContentTicketHandler,
    GetDocumentContentHandler,
    GetUserHandler,
    ListUsersHandler,
    GetCurrentUserHandler,
    CreateAccessListHandler,
    ListProjectAccessListsHandler,
    DeleteAccessListHandler,
    AssignAccessListHandler,
    SetProjectAccessHandler,
    CreateProjectGroupHandler,
    DeleteProjectGroupHandler,
    ListProjectGroupsHandler,
    JoinProjectGroupHandler,
    LeaveProjectGroupHandler,
    ListProjectGroupMembersHandler,
    CreateProjectTaskHandler,
    ListProjectTasksHandler,
    GetProjectTaskHandler,
    SetProjectTaskStatusHandler,
)
from presentation.http.middleware.extratctors.auth_info.bearer import (
    BearerAuthInfoExtractor,
)
from presentation.http.middleware.extratctors import AuthInfoExtractor


class PresentationProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def provide_jwt_presentation(self, settings: Settings) -> JwtAuthInfoPresenter:
        return JwtAuthInfoPresenter(
            public_key=settings.auth.public_key.read_text(),
            algorithm=settings.auth.algorithm,
        )

    @provide(scope=Scope.APP)
    def provide_jwt_ticket_presentation(
        self, settings: Settings
    ) -> JwtContentTicketPresenter:
        return JwtContentTicketPresenter(
            private_key=settings.auth.private_key.read_text(),
            algorithm=settings.auth.algorithm,
        )

    @provide(scope=Scope.APP)
    def provide_ticket_presentation(
        self, presenter: JwtContentTicketPresenter
    ) -> ContentTicketPresenter:
        return presenter

    @provide(scope=Scope.APP)
    def provide_auth_info_presentation(
        self, presenter: JwtAuthInfoPresenter
    ) -> AuthInfoPresenter:
        return presenter

    auth_info_extractor = provide(
        source=BearerAuthInfoExtractor, provides=AuthInfoExtractor, scope=Scope.APP
    )

    create_project_handler = provide(CreateProjectHandler)
    orders_presenter = provide(OrdersPresenter)
    list_projects_handler = provide(ListProjectsHandler)
    update_project_handler = provide(UpdateProjectHandler)
    delete_project_handler = provide(DeleteProjectHandler)
    create_user_handler = provide(CreateUserHandler)
    add_project_member_handler = provide(AddProjectMemberHandler)
    list_project_members_handler = provide(ListProjectMembersHandler)
    remove_project_member_handler = provide(RemoveProjectMemberHandler)
    list_current_user_projects_handler = provide(ListCurrentUserProjectsHandler)
    grant_owner_handler = provide(GrantOwnerHandler)
    set_role_handler = provide(SetMemberRoleHandler)
    create_directory_handler = provide(CreateDirectoryHandler)
    create_document_handler = provide(CreateDocumentHandler)
    delete_document_handler = provide(DeleteDocumentHandler)
    delete_directory_handler = provide(DeleteDirectoryHandler)
    create_ticket_handler = provide(CreateContentTicketHandler)
    get_document_content_handler = provide(GetDocumentContentHandler)
    get_user_handler = provide(GetUserHandler)
    list_users_handler = provide(ListUsersHandler)
    get_current_user_handler = provide(GetCurrentUserHandler)
    access_list_create_rule_responsible_presenter = provide(
        AccessListCreateRuleResponsiblePresenter
    )
    project_task_assignee_presenter = provide(ProjectTaskAssigneePresenter)
    create_access_list_handler = provide(CreateAccessListHandler)
    list_access_lists_handler = provide(ListProjectAccessListsHandler)
    delete_access_list_handler = provide(DeleteAccessListHandler)
    assign_access_list_handler = provide(AssignAccessListHandler)
    set_project_access_handler = provide(SetProjectAccessHandler)
    create_project_group_handler = provide(CreateProjectGroupHandler)
    delete_project_group_handler = provide(DeleteProjectGroupHandler)
    list_project_groups_handler = provide(ListProjectGroupsHandler)
    join_project_group_handler = provide(JoinProjectGroupHandler)
    leave_project_group_handler = provide(LeaveProjectGroupHandler)
    list_project_group_members_handler = provide(ListProjectGroupMembersHandler)
    create_project_task_handler = provide(CreateProjectTaskHandler)
    list_project_tasks_handler = provide(ListProjectTasksHandler)
    get_project_task_handler = provide(GetProjectTaskHandler)
    set_project_task_status_handler = provide(SetProjectTaskStatusHandler)

    @provide
    def provide_list_dir_content(
        self, usecase: ListDirectoryContentCompostion, presenter: OrdersPresenter
    ) -> ListDirectoryContentHandler:
        return ListDirectoryContentHandler(
            usecase, PydanticProjectUnitVisitor(), presenter
        )
