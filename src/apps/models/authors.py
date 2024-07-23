# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String

# Python
from typing import TYPE_CHECKING

# Local
from .base import Base


if TYPE_CHECKING:
    from .books import Book


class Author(Base):
    """Model for Authors."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="author", lazy="selectin"
    )
