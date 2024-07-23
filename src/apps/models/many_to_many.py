# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey

# Local
from .base import Base


class BookGenre(Base):
    """Many-to-many relationship between books and genres."""

    __tablename__ = "books_genres"

    book_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("books.id"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("genres.id"), primary_key=True
    )
