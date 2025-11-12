from datetime import timedelta
from dishka import Provider, provide, Scope, from_context
from setup.config import Settings


class DomainProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)