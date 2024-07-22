# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Integer, ForeignKey

# Local
from src.apps.abstract.models import Base


class Book(Base):
    """Model for Books."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer, index=True)
    pages: Mapped[int] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("authors.id")
    )
    genres = relationship(
        "Genre",
        secondary="book_genre",
        back_populates="books",
        lazy="selectin"
    )
