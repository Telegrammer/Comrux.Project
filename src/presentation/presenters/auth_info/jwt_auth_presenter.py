__all__ = ["JwtAuthInfoPresenter"]


from typing import Any

import jwt

from application.exceptions import ExpiredAccessKeyError
from presentation.exceptions import InvalidTokenTypeError


from presentation.models import AuthInfo
from presentation.constans import TokenType

from .base import AuthInfoPresenter


class JwtAuthInfoPresenter(AuthInfoPresenter):
    def __init__(
        self,
        public_key: str,
        algorithm: str,
    ):
        self._public_key: str = public_key
        self._algorithm: str = algorithm

    def _decode(self, credentials: bytes) -> dict[str, Any]:
        return jwt.decode(
            jwt=credentials, key=self._public_key, algorithms=self._algorithm
        )

    def to_auth_info[bytes](
        self, credentials: bytes, reqiered_type: TokenType = TokenType.ACCESS
    ) -> AuthInfo:
        try:
            payload: dict[str, Any] = self._decode(credentials)
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredAccessKeyError("Given Access key is expired")

        if (
            reqiered_type != TokenType.ANY
            and payload.get("type", None) != reqiered_type
        ):
            raise InvalidTokenTypeError(f"Token is not {reqiered_type}")

        return AuthInfo(
            key_id=payload["sub"],
            user_id=payload.get("user_id", None),
            created_at=payload.get("iat", None),
            expire_at=payload.get("exp", None),
        )

    def validate[bytes](self, raw_data: bytes, required_type: TokenType):
        return super().validate(raw_data, required_type)
