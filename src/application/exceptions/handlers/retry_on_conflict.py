from typing import Awaitable, Callable
import functools
import asyncio

from application.exceptions import InconsistentDataError


def retry_on_conflict(max_attempts: int = 3, delay: float = 2.0):

    def decorator[**P, T](func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:

            attempts: int = 0
            while True:
                try:
                    response: T = await func(*args, **kwargs)
                    return response
                except InconsistentDataError:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    asyncio.sleep(delay ** (attempts - 1))

        return wrapper

    return decorator
