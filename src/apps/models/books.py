# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Integer, ForeignKey

# Python
from typing import TYPE_CHECKING

# Local
from .base import Base
from .many_to_many import BookGenre


if TYPE_CHECKING:
    from .genres import Genre
    from .authors import Author


class Book(Base):
    """Model for Books."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    price: Mapped[int] = mapped_column(Integer, index=True)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    author_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(
            "authors.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
    )
    genre_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(
            "genres.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
    )
    author: Mapped["Author"] = relationship(
        "Author", back_populates="books", lazy="selectin"
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary="books_genres",
        back_populates="books", lazy="selectin"
    )
