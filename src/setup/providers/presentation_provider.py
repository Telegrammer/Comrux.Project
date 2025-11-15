__all__ = ["PresentationProvider"]


from datetime import timedelta
from typing import Type
from dishka import Provider, provide, Scope, from_context, AsyncContainer
from setup.config import Settings


from presentation.presenters import (
    OrdersPresenter,
)
from presentation.handlers import (
    CreateProjectHandler,
    ListProjectsHandler,
)


class PresentationProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    create_project_handler = provide(CreateProjectHandler)
    orders_presenter = provide(OrdersPresenter)
    list_projects_handler = provide(ListProjectsHandler)
