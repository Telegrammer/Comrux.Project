from dishka import Provider, provide, Scope, from_context
from setup.config import Settings
from datetime import timedelta

from domain.policies import TaskPolicy
from domain.services import TaskService
from domain.ports import (
    TaskIdGenerator,
)
from infrastructure.adapters import (
    TaskUuid4Generator,
)


class DomainProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    task_id_generator = provide(source=TaskUuid4Generator, provides=TaskIdGenerator)

    @provide
    def provide_task_policy(self) -> TaskPolicy:
        return TaskPolicy(
            init_resend_delta=timedelta(seconds=10),
            backoff_value=0.1,
            max_attempt_count=3,
        )

    task_service = provide(TaskService)
