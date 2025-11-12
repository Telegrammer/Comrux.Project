from dishka import Provider, Scope, from_context, provide
from setup.config import Settings

class TransportProvider(Provider):

    scope =Scope.APP

    settings = from_context(Settings)
    