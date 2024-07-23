# Pydantic
from pydantic import BaseModel


class ResponseSchema(BaseModel):
    """Schema just for response."""

    response: str | dict | BaseModel


class ErrorSchema(BaseModel):
    """Schema for error response."""

    error: str | dict
