__all__ = ["PresentationProvider"]


from datetime import timedelta
from typing import Type
from dishka import Provider, provide, Scope, from_context, AsyncContainer
from setup.config import Settings


from presentation.presenters import (
    OrdersPresenter,
    AuthInfoPresenter,
    JwtAuthInfoPresenter,
)
from presentation.models import AuthInfo
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
