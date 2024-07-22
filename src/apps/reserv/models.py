# SqlAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, Date, Boolean

# Python
from datetime import date

# Local
from src.apps.abstract.models import Base


class BookReservation(Base):
    """Model for reservation books"""

    __tablename__ = "reserv"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    book_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("books.id"))
    begin_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    on_hands: Mapped[bool] = mapped_column(Boolean, default=True)
    is_returned: Mapped[bool] = mapped_column(Boolean, default=False)
    user = relationship("User", lazy="selectin")
    book = relationship("Book", lazy="selectin")
