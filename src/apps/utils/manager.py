# FastApi
from fastapi import Depends, Response, Request

# Third-Party
from fastapi_users import (
    BaseUserManager, IntegerIDMixin, InvalidPasswordException,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users import exceptions
from sqlalchemy.ext.asyncio import AsyncSession

# Python
from typing import Optional

# Local
from src.apps.models.users import User
from src.apps.schemas.users import UserLogin
from .session import get_async_session
from src.settings.base import logger


SECRET = "SECRET"


async def get_user_db(conn: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(conn, User)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    @staticmethod
    async def on_after_register(user: User, response: Response = None):
        logger.info(msg=f"User {user.id} has registered.")

    @staticmethod
    async def on_after_forgot_password(user: User, token: str):
        logger.info(msg=f"User {user.id} has forgot their password."
            f"Reset token: {token}")

    @staticmethod
    async def on_after_request_verify(user: User, token: str):
        logger.info(msg=f"Verification requested for user {user.id}."
            f"Verification token: {token}")
        
    @staticmethod
    async def validate_password(password: str, user: User):
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
    
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
    
    @staticmethod
    async def on_after_login(
        user: User, request: Optional[Request] = None, 
        response: Response = None
    ):
        logger.info(msg=f"User {user.id} logged in.")

    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        logger.info(msg=f"User {user.id} has been verified")

    async def authenticate(self, credentials: UserLogin) -> User | None:
        try:
            user = await self.get_by_email(credentials.email)
        except exceptions.UserNotExists:
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = \
            self.password_helper.verify_and_update(
                credentials.password, user.hashed_password
            )
        if not verified:
            return None
        if updated_password_hash is not None:
            await self.user_db.update(
                user, {"hashed_password": updated_password_hash}
            )

        return user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
