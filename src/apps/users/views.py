# FastApi
from fastapi import (
    Form, UploadFile, APIRouter, Depends, status, HTTPException
)

# Third-Party
from fastapi_users import exceptions, models, FastAPIUsers
from fastapi_users.authentication import JWTStrategy
from fastapi_users.authentication import Authenticator
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from PIL import Image

# Python
from typing import Annotated, Tuple
import io
import os

# Local
from src.settings.const import VOLUME
from src.apps.abstract.jwt_backend import auth_backend, get_jwt_strategy
from .manager import get_user_manager, UserManager
from .models import User
from .schemas import UserCreate, UserRead, UserLogin


class Registration:
    """View for Registration."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/auth", tags=["Auth module"])
        self.router.add_api_route(
            path="/reg", endpoint=self.register, methods=["POST"],
            response_model=UserRead,
            status_code=status.HTTP_201_CREATED,
            responses={400: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        })

    async def register(
        self, email: Annotated[str, Form()], 
        password: Annotated[str, Form()],
        first_name: Annotated[str, Form()],
        last_name: Annotated[str, Form()],
        avatar: UploadFile,
        user_manager: UserManager = Depends(get_user_manager),
    ):
        try:
            image = Image.open(io.BytesIO(await avatar.read()))
            avatar_filename = f"users/{email}_{avatar.filename}"
            avatar_path = os.path.join(VOLUME, avatar_filename)
            os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
            schema = UserCreate(
                email=email, password=password, first_name=first_name,
                last_name=last_name, avatar=avatar_path
            )
            image.save(avatar_path)
            created_user = await user_manager.create(
                user_create=schema, safe=True
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        schema = UserRead.model_validate(obj=created_user)
        return schema


class LoginLogout:
    """View for login and logout."""

    fastapi_users = FastAPIUsers[User, int](
        get_user_manager, [auth_backend]
    )

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                    }
                }
            },
        },
        **auth_backend.transport.get_openapi_login_responses_success(),
    }
    logout_responses: OpenAPIResponseType = {
        **{
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
        **auth_backend.transport.get_openapi_logout_responses_success(),
    }

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/auth", tags=["Auth module"])
        self.router.add_api_route(
            path="/login", endpoint=self.login, methods=["POST"],
            responses=self.login_responses
        )
        self.router.add_api_route(
            path="/logout", endpoint=self.logout, methods=["POST"],
            responses=self.logout_responses
        )

    get_current_user_token = fastapi_users.authenticator.current_user_token(
        active=True
    )

    async def login(
        self, credentials: UserLogin,
        user_manager: UserManager = Depends(get_user_manager),
        strategy: JWTStrategy = Depends(get_jwt_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        response = await auth_backend.login(strategy, user)
        await user_manager.on_after_login(user, response)
        return response

    async def logout(
        self, strategy: JWTStrategy = Depends(get_jwt_strategy),
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
    ):
        user, token = user_token
        return await auth_backend.logout(strategy, user, token)
    

reg = Registration()
login_logout = LoginLogout()
