__all__ = ["ApplicationProvider"]


from dishka import Provider, provide, Scope, from_context
from setup.config import Settings

from application.compositions import (
    ProcessTasksComposition,
)
from application.ports import Clock, TaskNotifier
from application.ports.mappers import (
    TaskMapper,
)
from application.ports.gateways import (
    TaskCommandGateway,
)
from infrastructure.adapters import (
    TimestampClock,
    KafkaTaskNotifier,
)
from infrastructure.adapters.mappers import (
    SqlAlchemyTaskMapper,
)
from infrastructure.adapters.gateways import (
    SQLAlchemyQueryBuilder,
    SqlAlchemyTaskCommandGateway,
)
from infrastructure.adapters.task_polling_worker import TaskPollingWorker


class ApplicationProvider(Provider):
    scope = Scope.REQUEST
    settings = from_context(Settings, scope=Scope.APP)

    clock = provide(source=TimestampClock, provides=Clock)

    @provide
    def provide_query_builder(self) -> SQLAlchemyQueryBuilder:
        return SQLAlchemyQueryBuilder()

    task_mapper = provide(source=SqlAlchemyTaskMapper, provides=TaskMapper)
    task_gateway = provide(
        source=SqlAlchemyTaskCommandGateway, provides=TaskCommandGateway
    )
    task_notifier = provide(source=KafkaTaskNotifier, provides=TaskNotifier)

    process_task_composition = provide(ProcessTasksComposition)

    @provide
    def provide_polling_worker(
        self,
        worker: ProcessTasksComposition,
        clock: Clock,
    ) -> TaskPollingWorker:
        return TaskPollingWorker(
            clock=clock, worker=worker, poll_interval=3.0, batch_size=10
        )
