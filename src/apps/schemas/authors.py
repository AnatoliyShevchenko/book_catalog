# Pydantic
from pydantic import BaseModel, Field

# Python
from typing import Optional


class AuthorSchema(BaseModel):
    """Schema for view Author."""

    id: int = Field(ge=0)
    first_name: str = Field(...)
    last_name: str = Field(...)
    avatar: str | None


class AllAuthorsSchema(BaseModel):
    """Schema for view all Authors."""

    response: list[AuthorSchema]


class CreateAuthorSchema(BaseModel):
    """Schema for create or update Author."""

    first_name: str = Field(...)
    last_name: str = Field(...)
    avatar: str | None
