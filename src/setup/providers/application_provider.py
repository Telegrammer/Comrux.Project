from dishka import Provider, provide, Scope, from_context
from functools import partial
from typing import Callable
from setup.config import Settings


class ApplicationProvider(Provider):
    scope = Scope.REQUEST
    settings = from_context(Settings, scope=Scope.APP)