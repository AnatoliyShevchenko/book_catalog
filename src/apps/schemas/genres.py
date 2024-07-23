# Pydantic
from pydantic import BaseModel, Field


class GenreSchema(BaseModel):
    """Schema for view Genre."""

    id: int = Field(ge=0)
    title: str = Field(...)


class AllGenresSchema(BaseModel):
    """Schema for view all Genres."""

    response: list[GenreSchema]


class CreateGenreSchema(BaseModel):
    """Schema for create or update Genre."""

    title: str = Field(...)
