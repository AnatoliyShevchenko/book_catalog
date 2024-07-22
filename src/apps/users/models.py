# FastAPI-Users
from fastapi_users.db import SQLAlchemyBaseUserTable

# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String

# Local
from src.apps.abstract.models import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    """Model for Users."""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    avatar: Mapped[str] = mapped_column(String)
