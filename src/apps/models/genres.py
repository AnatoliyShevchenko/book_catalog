# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String

# Python
from typing import TYPE_CHECKING

# Local
from .base import Base
from .many_to_many import BookGenre


if TYPE_CHECKING:
    from .books import Book


class Genre(Base):
    """Model for Genres."""

    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    books: Mapped[list["Book"]] = relationship(
        secondary="books_genres",
        back_populates="genres", lazy="selectin"
    )
