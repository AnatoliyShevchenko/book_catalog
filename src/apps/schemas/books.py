# Pydantic
from pydantic import BaseModel, Field

# Python
from typing import Optional

# Local
from .genres import GenreSchema
from .authors import AuthorSchema


class BookSchema(BaseModel):
    """Schema for view book."""

    id: int = Field(ge=0)
    title: str = Field(...)
    price: int = Field(ge=0)
    pages: int = Field(ge=0, le=5000)
    author: AuthorSchema
    genre: list[GenreSchema]


class AllBooksSchema(BaseModel):
    """Schema for all books view."""

    response: list[BookSchema]


class CreateBookSchema(BaseModel):
    """Schema for create book."""

    title: str = Field(...)
    price: int = Field(ge=0)
    pages: int = Field(ge=0, le=5000)
    author_id: int = Field(ge=0)
    genre_id: int = Field(ge=0)
    

class UpdateBookSchema(BaseModel):
    """Schema for update Book."""

    title: Optional[str] = None
    price: Optional[int] = None
    pages: Optional[int] = None
    author_id: Optional[int] = None
    genre_id: Optional[int] = None


class ZipBookSchema(BaseModel):
    id: int = Field(ge=0)
    title: str = Field(...)
    price: int = Field(ge=0)
    pages: int = Field(ge=0, le=5000)
    author_id: int = Field(ge=0)
    genre_id: int = Field(ge=0)
