# FastApi
from fastapi import (
    Form, UploadFile, APIRouter, Depends, 
    status, HTTPException, Response, File
)

# Third-Party
from fastapi_users import exceptions, models, FastAPIUsers
from fastapi_users.authentication import JWTStrategy
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update
from PIL import Image

# Python
from typing import Annotated, Tuple, Optional
import io
import os

# Local
from src.settings.const import VOLUME
from src.apps.utils.jwt_backend import auth_backend, get_jwt_strategy
from src.apps.utils.session import get_async_session
from src.apps.utils.manager import get_user_manager, UserManager
from src.apps.models.users import User
from src.apps.schemas.users import (
    UserCreate, UserRead, UserLogin, AllUsersSchema,
)
from src.apps.schemas.response import ResponseSchema, ErrorSchema


class Registration:
    """View for Registration."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/auth", tags=["Users module"])
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
        self.router.add_api_route(
            path="/users/{user_id}", endpoint=self.remove_user,
            methods=["DELETE"], responses={
                200: {"model": ResponseSchema},
                404: {"model": None}
            }
        )
        self.router.add_api_route(
            path="/users/", endpoint=self.get_all_users, 
            description="""Get all users with pagination,
            pages begining by 0""",
            methods=["GET"], responses={
                200: {"model": AllUsersSchema},
                204: {"model": None}
            }
        )
        self.router.add_api_route(
            path="users/{user_id}", endpoint=self.get_user,
            methods=["GET"], responses={
                200: {"model": UserRead},
                204: {"model": None}
            }
        )
        self.router.add_api_route(
            path="/users/{user_id}", endpoint=self.update_user, 
            methods=["PUT"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema},
                404: {"model": None}
            }
        )

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
    
    async def remove_user(
        self, user_id: int,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(User).where(User.id == user_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(
                response=f"Author {user_id} is removed!"
            )
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    async def get_all_users(
        self, page_number: int = 0, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(User).limit(50).offset(page_number)
        temp = await session.execute(query)
        data = temp.scalars().all()
        if not data:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        obj = []
        for item in data:
            obj.append(UserRead(
                id=item.id, first_name=item.first_name, email=item.email,
                last_name=item.last_name, avatar=item.avatar
            ))
        result = AllUsersSchema(response=obj)
        return result
    
    async def get_user(
        self, user_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(User).where(User.id == user_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if not data:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        result = UserRead(
            id=data.id, email=data.email, is_active=data.is_active, 
            is_superuser=data.is_superuser, is_verified=data.is_verified,
            first_name=data.first_name, last_name=data.last_name
        )
        return result
    
    async def update_user(
        self, user_id: int, response: Response,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        avatar: Optional[UploadFile] = File(None), 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(User).where(User.id == user_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            update_values = {}
            if first_name:
                update_values['first_name'] = first_name
            if last_name:
                update_values['last_name'] = last_name
            if avatar:
                image = Image.open(io.BytesIO(await avatar.read()))
                name = os.urandom(32).hex()
                avatar_filename = f"users/{name}"
                avatar_path = os.path.join(VOLUME, avatar_filename)
                os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
                update_values['avatar'] = avatar_path
                image.save(avatar_path)
            if not update_values:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorSchema(error="No fields to update")

            try:
                stmt = update(User).where(
                    User.id == user_id
                ).values(**update_values)
                await session.execute(statement=stmt)
                await session.commit()
                return ResponseSchema(
                    response=f"User {user_id} is updated!"
                )
            except Exception as e:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorSchema(error=str(e))
        return Response(status_code=status.HTTP_404_NOT_FOUND)


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
