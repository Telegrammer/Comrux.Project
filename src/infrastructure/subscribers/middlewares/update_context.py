from typing import Type, Callable, Awaitable

from dishka import AsyncContainer
from faststream import ContextRepo
from faststream.types import SendableMessage

from utils.merge_context import merge_context


async def update_context(
    call_next: Callable[[SendableMessage], Awaitable[SendableMessage]],
    msg: SendableMessage,
    new_injections: dict[Type, object],
    context: ContextRepo,
) -> SendableMessage:
    old_container: AsyncContainer = context.get("dishka")
    app_container: AsyncContainer = old_container.parent_container
    async with app_container(
        context=merge_context(old_container, new_injections)
    ) as new_container:
        context.set_local("dishka", new_container)
        return await call_next(msg)
