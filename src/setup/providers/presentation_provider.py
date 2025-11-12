from datetime import timedelta
from typing import Type
from dishka import Provider, provide, Scope, from_context, AsyncContainer
from setup.config import Settings


class PresentationProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)
