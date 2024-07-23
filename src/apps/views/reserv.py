# FastApi
from fastapi import Depends, APIRouter, Response, status

# Thirt-Party
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, insert, update

# Python
from typing import Literal
from datetime import date, datetime

# Local
from src.apps.utils.session import get_async_session
from src.apps.models.reserv import BookReservation
from src.apps.models.users import User
from src.apps.models.books import Book
from src.apps.schemas.users import UserRead
from src.apps.schemas.books import ZipBookSchema
from src.apps.schemas.reserv import (
    GetReservationSchema, AllReservationsSchema,
    CreateReserveSchema,
)
from src.apps.schemas.response import ResponseSchema, ErrorSchema
from src.apps.utils.jwt_backend import current_user


class BookReserv:
    """CRUD for Book Reservation."""

    def __init__(self) -> None:
        self.path = "/reserv"
        self.router = APIRouter(
            prefix="/api/v1", tags=["Book Reservation CRUD"]
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.get_all_reservations,
            methods=["GET"], responses={
                200: {"model": AllReservationsSchema},
                204: {"model": None},
                400: {"model": ErrorSchema}
            }
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.make_reserv, methods=["POST"],
            responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema},
                401: {"model": None}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{reserv_id}", endpoint=self.return_book, 
            methods=["PUT"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema},
                401: {"model": None}
            }
        )

    async def get_all_reservations(
        self, response: Response, book_title: str = None,
        start_date: date | str = None, 
        end_date: date | str = None, 
        page_number: int = 0,
        on_hands: Literal["True", "False"] = None,
        is_returned: Literal["True", "False"] = None,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(BookReservation)
        conditions = []
        if start_date:
            if isinstance(start_date, str):
                try:
                    temp = date.fromisoformat(start_date)
                    conditions.append(BookReservation.begin_date <= temp)
                    conditions.append(BookReservation.end_date >= temp)
                except Exception as e:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return ErrorSchema(error=str(e))
            else:
                conditions.append(BookReservation.begin_date <= start_date)
                conditions.append(BookReservation.end_date >= start_date)
        if end_date:
            if isinstance(end_date, str):
                try:
                    temp = date.fromisoformat(end_date)
                    conditions.append(BookReservation.begin_date <= temp)
                    conditions.append(BookReservation.end_date >= temp)
                except Exception as e:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return ErrorSchema(error=str(e))
            else:
                conditions.append(BookReservation.begin_date <= end_date)
                conditions.append(BookReservation.end_date >= end_date)

        if on_hands == "True" and is_returned == "True":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorSchema(
                error="Book cannot be on hands and returned at the same moment!"
            )
        elif on_hands == "True":
            conditions.append(BookReservation.on_hands == True)
        elif is_returned == "True":
            conditions.append(BookReservation.is_returned == True)

        if book_title:
            conditions.append(BookReservation.book.has(title=book_title))

        if len(conditions) > 1:
            query = query.where(and_(*conditions))
        elif len(conditions) == 1:
            query = query.where(conditions[0])

        query = query.limit(50).offset(page_number)
        temp = await session.execute(query)
        data = temp.scalars().all()
        if not data:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        obj = []
        for item in data:
            user: User = item.user
            book: Book = item.book
            user_schema = UserRead(
                id=user.id, email=user.email, avatar=user.avatar,
                first_name=user.first_name, last_name=user.last_name
            )
            book_schema = ZipBookSchema(
                id=book.id, title=book.title, pages=book.pages, 
                price=book.price, author_id=book.author_id, 
                genre_id=book.genre_id
            )
            obj.append(GetReservationSchema(
                id=item.id, begin_date=item.begin_date, 
                end_date=item.end_date, on_hands=item.on_hands, 
                is_returned=item.is_returned, user=user_schema,
                book=book_schema
            ))
        result = AllReservationsSchema(response=obj)
        return result
    
    async def make_reserv(
        self, obj: CreateReserveSchema, response: Response,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
    ):
        if not user:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        user_id = user.id
        schema = CreateReserveSchema.model_validate(obj=obj)
        query = select(BookReservation).where(and_(
            BookReservation.book_id == schema.book_id,
            BookReservation.begin_date <= schema.begin_date,
            BookReservation.end_date >= schema.begin_date,
            BookReservation.on_hands == True
        ))
        temp = await session.execute(query)
        data = temp.scalars().all()
        if data:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorSchema(error="Книга уже занята")
        stmt = insert(BookReservation).values(
            user_id=user_id, book_id=schema.book_id,
            begin_date=schema.begin_date, end_date=schema.end_date
        )
        await session.execute(statement=stmt)
        await session.commit()
        return ResponseSchema(response="Книга успешно забронирована!")
    
    async def return_book(
        self, reserv_id: int, user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
    ):
        if not user:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        now = datetime.now()
        query = select(BookReservation).where(and_(
            BookReservation.id == reserv_id,
            BookReservation.end_date >= now.date(),
            BookReservation.on_hands == True
        ))
        temp = await session.execute(query)
        data = temp.scalars().all()
        if data:
            stmt = update(BookReservation).where(
                BookReservation.id == reserv_id
            ).values(on_hands=False, is_returned=True)
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(
                response="Спасибо, берите еще что нибудь"
            )
        return Response(status_code=status.HTTP_404_NOT_FOUND)



reserv = BookReserv()
