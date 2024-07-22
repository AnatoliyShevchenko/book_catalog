# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Integer, ForeignKey

# Local
from src.apps.abstract.models import Base


class Genre(Base):
    """Model for Genres."""

    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    books = relationship(
        "Book",
        secondary="book_genre",
        back_populates="genres",
        lazy="selectin"
    )
