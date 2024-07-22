# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String

# Local
from src.apps.abstract.models import Base


class User(Base):
    """Model for Users."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    avatar: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
