import logging
import sys
from faststream.kafka import KafkaBroker
from dishka import make_async_container
from setup import (
    DatabaseProvider,
    TransportProvider,
)
from setup.providers.outbox_worker import (
    DomainProvider,
    ApplicationProvider,
)

from setup.config import settings, Settings

from infrastructure.adapters.task_polling_worker import TaskPollingWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],  # Явно говорим писать в консоль
)
logger = logging.getLogger("outbox_worker")
logger.setLevel(logging.INFO)


async def main():
    async with KafkaBroker(
        str(settings.transport.kafka_url).replace("kafka://", "")
    ) as broker:
        container = make_async_container(
            DatabaseProvider(),
            DomainProvider(),
            ApplicationProvider(),
            TransportProvider(),
            context={Settings: settings, KafkaBroker: broker},
        )
        async with container() as scope:
            runner = await scope.get(TaskPollingWorker)
            logging.info("Worker created")
            await runner.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
