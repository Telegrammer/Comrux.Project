from contextlib import asynccontextmanager
from dishka import make_async_container, AsyncContainer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import dishka.integrations.fastapi as fastapi_integration
import dishka.integrations.faststream as faststream_integration
from faststream.kafka import KafkaBroker
from faststream import ContextRepo, FastStream
import logging

from setup import (
    Settings,
    settings,
    DatabaseHelper,
    DatabaseProvider,
    ApplicationProvider,
    DomainProvider,
    PresentationProvider,
)


from presentation.http import (
    projects_router,
    users_router,
)
from presentation.http.middleware import (
    InjectAuthInfoMiddleware,
    InjectCurrentUserIdMiddleware,
)
from infrastructure.subscribers.users import user_created_sub_router
from infrastructure.subscribers.middlewares import InjectUserIdFromMessageMiddleware


logger = logging.getLogger("__name__")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def create_app() -> FastAPI:
    broker = KafkaBroker(str(settings.transport.kafka_url).replace("kafka://", ""))
    container: AsyncContainer = make_async_container(
        DatabaseProvider(),
        DomainProvider(),
        ApplicationProvider(),
        PresentationProvider(),
        context={Settings: settings, KafkaBroker: broker},
    )

    broker.include_router(user_created_sub_router)
    faststream_integration.setup_dishka(
        container, FastStream(broker, context=ContextRepo())
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with container() as app_state:
            app.state.container = app_state
            await broker.start()
        yield
        db_helper = await container.get(DatabaseHelper)
        await db_helper.dispose()
        await broker.stop()

    app = FastAPI(lifespan=lifespan)
    app.include_router(projects_router)
    app.include_router(users_router)

    broker.add_middleware(InjectUserIdFromMessageMiddleware)
    app.add_middleware(InjectCurrentUserIdMiddleware)
    app.add_middleware(InjectAuthInfoMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_integration.setup_dishka(container=container, app=app)
    logger.info("App created")
    return app
