# Third-Party
from fastapi_users import schemas
from pydantic import EmailStr, BaseModel, Field

# Python
from typing import Optional


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    first_name: str
    last_name: str
    avatar: str


class AllUsersSchema(BaseModel):
    response: list[UserRead]


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    first_name: str
    last_name: str
    avatar: str


class UserUpdate(schemas.BaseUserUpdate):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    