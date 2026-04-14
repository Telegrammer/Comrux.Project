import logging

from dishka.integrations.faststream import FromDishka, inject
from faststream.kafka import KafkaRouter

from application.export import BuildProjectReleaseComposition
from .messages import ProjectReleaseCreatedMessage

logger = logging.getLogger(__name__)

project_release_created_sub_router = KafkaRouter()


@project_release_created_sub_router.subscriber(
    "project.releases.created",
    group_id="project-release-worker",
    auto_offset_reset="earliest",
)
@inject
async def build_project_release(
    usecase: FromDishka[BuildProjectReleaseComposition],
    message: ProjectReleaseCreatedMessage,
) -> None:
    await usecase(
        project_id=message.project_id,
        release_id=message.release_id,
    )
