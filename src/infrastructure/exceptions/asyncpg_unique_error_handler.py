__all__ = ["unique_violation_aware"]


import logging
import functools

from typing import Callable, Awaitable
from sqlalchemy.exc import IntegrityError
from asyncpg import UniqueViolationError


from application.ports.gateways.errors import GatewayFailedError
from application.exceptions import ApplicationError

logger = logging.getLogger(__name__)


def unique_violation_aware(model_error: ApplicationError):

    def decorator[**P, T](
        command: Callable[P, Awaitable[T]],
    ) -> Callable[P, Awaitable[T]]:

        @functools.wraps(command)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                target_name: str = command.__qualname__
                return await command(*args, **kwargs)
            except IntegrityError as e:
                original_error = e.orig
                if (
                    getattr(original_error, "sqlstate", None)
                    != UniqueViolationError.sqlstate
                ):
                    logger.exception(
                        "An IntegrityError occurred in '%s', but it was not a UniqueViolation. Re-raising.",
                        target_name,
                    )
                    raise

                error_detail: str = str(original_error).split("\n")[1]
                logger.warning(
                    "UniqueViolationError detected in function/method '%s'. Converting to application error '%s'. Error details: %s",
                    target_name,
                    model_error.__name__,
                    error_detail,
                )
                if error_detail.startswith("DETAIL:  Key (id_)"):
                    raise GatewayFailedError(
                        "Somehow object was created with the same id. Please try again"
                    )

                raise model_error

        return wrapper

    return decorator
