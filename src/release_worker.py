import asyncio
import logging
import sys

from dishka import make_async_container
import dishka.integrations.faststream as faststream_integration
from faststream import ContextRepo, FastStream
from faststream.kafka import KafkaBroker

from infrastructure.export import project_release_created_sub_router
from setup import Settings, settings
from setup.providers import (
    ApplicationProvider,
    DatabaseProvider,
    DomainProvider,
    ExportApplicationProvider,
    ExportDomainProvider,
    TransportProvider,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def main() -> None:
    broker = KafkaBroker(str(settings.transport.kafka_url).replace("kafka://", ""))
    broker.include_router(project_release_created_sub_router)

    container = make_async_container(
        DatabaseProvider(),
        DomainProvider(),
        ApplicationProvider(),
        ExportDomainProvider(),
        ExportApplicationProvider(),
        TransportProvider(),
        context={Settings: settings, KafkaBroker: broker},
    )

    faststream_integration.setup_dishka(
        container,
        FastStream(broker, context=ContextRepo()),
    )

    await broker.start()
    try:
        await asyncio.Event().wait()
    finally:
        await broker.stop()
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
