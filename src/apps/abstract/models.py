# SqlAlchemy
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey


class Base(AsyncAttrs, DeclarativeBase):
    """Base model as parent for other models."""
    pass


class BookGenre(Base):
    """Many-to-many relationship between books and genres."""

    __tablename__ = "books_genres"

    book_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("books.id"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("genres.id"), primary_key=True
    )

