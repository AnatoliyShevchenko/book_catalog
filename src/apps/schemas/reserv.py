# Pydantic
from pydantic import BaseModel, Field

# Python
from datetime import date

# Local
from .users import UserRead
from .books import ZipBookSchema


class GetReservationSchema(BaseModel):
    id: int = Field(ge=0)
    begin_date: date = Field(...)
    end_date: date = Field(...)
    on_hands: bool = Field(...)
    is_returned: bool = Field(...)
    user: UserRead
    book: ZipBookSchema


class AllReservationsSchema(BaseModel):
    response: list[GetReservationSchema]
    

class CreateReserveSchema(BaseModel):
    book_id: int = Field(ge=0)
    begin_date: date = Field(...)
    end_date: date = Field(...)
