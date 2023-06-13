import uuid
from typing import Optional
import jwt
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, IntegerIDMixin, exceptions, schemas, models
from fastapi_users.jwt import decode_jwt, generate_jwt

from api.utils.message_utils import send_verify_message, send_reset_message
from db.models import User
from db.session import get_user_db

SECRET = "SECRET"


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def forgot_password(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        """
        Start a forgot password request.

        Triggers the on_after_forgot_password handler on success.

        :param user: The user that forgot its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        """
        if not user.is_active:
            raise exceptions.UserInactive()

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
            self, token: str, password: str, request: Optional[Request] = None
    ) -> models.UP:
        """
        Reset the password of a user.

        Triggers the on_after_reset_password handler on success.

        :param token: The token generated by forgot_password.
        :param password: The new password to set.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises InvalidResetPasswordToken: The token is invalid or expired.
        :raises UserInactive: The user is inactive.
        :raises InvalidPasswordException: The password is invalid.
        :return: The user with updated password.
        """
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidResetPasswordToken()

        user = await self.get(parsed_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise exceptions.InvalidResetPasswordToken()

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        pass

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        send_reset_message(token, user.email)

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        send_verify_message(token, user.email)
