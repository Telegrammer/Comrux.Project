__all__ = ["InjectUserIdFromMessageMiddleware"]


from typing import Callable, Awaitable
from dishka import AsyncContainer
from faststream import BaseMiddleware
from faststream.types import SendableMessage
from domain import UserId
from domain.ports import UserIdGenerator
from .update_context import update_context
from utils.merge_context import merge_context
import json


class InjectUserIdFromMessageMiddleware(BaseMiddleware):

    async def consume_scope(
        self,
        call_next: Callable[[SendableMessage], Awaitable[SendableMessage]],
        msg: SendableMessage,
    ) -> SendableMessage:

        body = json.loads(getattr(msg, "body", None))
        if isinstance(body, dict) and "user_id" in body.keys():
            user_id = UserId(body["user_id"])
            return await update_context(
                call_next, msg, {UserIdGenerator: lambda: user_id}, self.context
            )

        return await call_next(msg)

    async def publish_scope(
        self,
        call_next: Callable[[SendableMessage], Awaitable[SendableMessage]],
        msg: SendableMessage,
    ) -> SendableMessage:
        return await call_next(msg)
