from contextlib import asynccontextmanager
from dishka import make_async_container, AsyncContainer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import dishka.integrations.fastapi as fastapi_integration
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


from presentation.http import projects_router


logger = logging.getLogger("__name__")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app() -> FastAPI:
    container: AsyncContainer = make_async_container(
        DatabaseProvider(),
        DomainProvider(),
        ApplicationProvider(),
        PresentationProvider(),
        context={Settings: settings},
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with container() as app_state:
            app.state.container = app_state
        yield
        db_helper = await container.get(DatabaseHelper)
        await db_helper.dispose()

    app = FastAPI(lifespan=lifespan)
    app.include_router(projects_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_integration.setup_dishka(container=container, app=app)
    logger.info("App created")
    return app
