# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String

# Local
from src.apps.abstract.models import Base


class Author(Base):
    """Model for Authors."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    avatar: Mapped[str] = mapped_column(String)
    books = relationship(
        "Book", back_populates="author", lazy="selectin"
    )
