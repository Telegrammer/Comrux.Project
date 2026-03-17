__all__ = ["sub_router"]


import logging
from dishka.integrations.faststream import FromDishka, inject
from faststream.kafka import KafkaRouter

from domain.exceptions import DomainFieldError
from application.exceptions import EntityAlreadyExistsError
from application.compositions import CreateUserComposition
from application.usecases import CreateUserRequest
from .models import UserCreated

logger = logging.getLogger(__name__)


user_created_sub_router = KafkaRouter()


@user_created_sub_router.subscriber(
    "user.created", group_id="project-service", auto_offset_reset="earliest"
)
@inject
async def create_user(usecase: FromDishka[CreateUserComposition], message: UserCreated):
    try:
        await usecase(
            CreateUserRequest.from_primitives(
                email=message.email,
                name=message.name,
                bio=message.bio,
                birthdate=message.birthdate,
            )
        )
    except KeyError:
        raise DomainFieldError("Recevied wrong data")
    except EntityAlreadyExistsError:
        logger.info("User object with id %s already exists", message.get("user_id"))
