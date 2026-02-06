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
)
from application.services import (
    CurrentUserService,
)
from application.ports import Clock
from application.ports.mappers import ProjectMapper, UserMapper
from application.ports.gateways import (
    ProjectCommandGateway,
    ProjectQueryGateway,
    UserCommandGateway,
    UserQueryGateway,
)
from infrastructure.adapters import TimestampClock
from infrastructure.adapters.mappers import (
    SqlAlchemyProjectMapper,
    SqlAlchemyUserMapper,
)
from infrastructure.adapters.gateways import (
    SqlAlchemyProjectCommandGateway,
    SqlAlchemyProjectQueryGateway,
    SqlAlchemyUserCommandGateway,
    SqlAlchemyUserQueryGateway,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST
    settings = from_context(Settings, scope=Scope.APP)
    user_id = from_context(UserId)

    clock = provide(source=TimestampClock, provides=Clock)

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

    project_mapper = provide(SqlAlchemyProjectMapper)

    project_command_gateway = provide(
        source=SqlAlchemyProjectCommandGateway, provides=ProjectCommandGateway
    )

    project_query_gateway = provide(
        source=SqlAlchemyProjectQueryGateway,
        provides=ProjectQueryGateway,
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
