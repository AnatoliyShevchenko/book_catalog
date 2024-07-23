# FastApi
from fastapi import Depends, APIRouter, Response, status

# Thirt-Party
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, insert, asc, desc

# Python
from typing import Literal

# Local
from src.apps.utils.session import get_async_session
from src.apps.models.books import Book
from src.apps.models.many_to_many import BookGenre
from src.apps.schemas.response import ResponseSchema, ErrorSchema
from src.apps.schemas.books import (
    BookSchema, CreateBookSchema, AllBooksSchema, UpdateBookSchema,
)
from src.apps.schemas.authors import AuthorSchema
from src.apps.schemas.genres import GenreSchema


class Books:
    """View for Books."""

    def __init__(self) -> None:
        self.path = "/books"
        self.router = APIRouter(
            prefix="/api/v1", tags=["Books CRUD"]
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.add_book, methods=["POST"],
            responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema}
            }
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.get_all_books, 
            description="""
            Эндпоинт возвращает все книги с сортировкой по 
            цене и с пагинацией. Пагинация начинается с нуля.""",
            methods=["GET"], responses={
                200: {"model": AllBooksSchema},
                404: {"model": None}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{book_id}", endpoint=self.remove_book,
            methods=["DELETE"], responses={
                200: {"model": ResponseSchema},
                404: {"model": None}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{book_id}", endpoint=self.update_book,
            methods=["PUT"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema},
                404: {"model": None}
            }
        )

    async def add_book(
        self, obj: CreateBookSchema, response: Response,
        session: AsyncSession = Depends(get_async_session)
    ):
        try:
            stmt = insert(Book).values(
                title=obj.title, price=obj.price, pages=obj.pages,
                author_id=obj.author_id, genre_id=obj.genre_id
            )
            await session.execute(statement=stmt)
            book_query = select(Book).where(Book.title == obj.title)
            result = await session.execute(book_query)
            book = result.scalar_one_or_none()

            if book:
                stmt = insert(BookGenre).values(
                    book_id=book.id, 
                    genre_id=obj.genre_id
                )
                await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(
                response=f"Book {obj.title} is created!"
            )
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorSchema(error=str(e))

    async def get_all_books(
        self, sort_by_price: Literal["asc", "desc"] = None, 
        page_number: int = 0, genre_id: int = None, 
        first_name: str = None, last_name: str = None,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Book)

        conditions = []
        if genre_id:
            conditions.append(Book.genre_id == genre_id)
        if first_name:
            conditions.append(Book.author.has(first_name=first_name))
        if last_name:
            conditions.append(Book.author.has(last_name=last_name))

        if len(conditions) > 1:
            query = query.where(and_(*conditions))
        elif len(conditions) == 1:
            query = query.where(conditions[0])

        if sort_by_price:
            query = query.order_by(asc(
                Book.price
            ) if sort_by_price == "asc" else desc(Book.price))


        query = query.limit(50).offset(page_number)
        temp = await session.execute(query)
        data = temp.scalars().all()
        if not data:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        obj = []
        for item in data:
            author = AuthorSchema(
                id=item.author.id, first_name=item.author.first_name, 
                last_name=item.author.last_name, avatar=item.author.avatar
            )
            genres = [
                GenreSchema(
                    id=genre.id, title=genre.title
                ) for genre in item.genres
            ]
            obj.append(BookSchema(
                id=item.id, title=item.title, price=item.price, 
                pages=item.pages, author=author, genre=genres
            ))
        result = AllBooksSchema(response=obj)
        return result
    
    async def remove_book(
        self, book_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Book).where(Book.id == book_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            stmt = delete(Book).where(Book.id == book_id)
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(
                response=f"Genre {book_id} is removed!"
            )
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    async def update_book(
        self, book_id: int, obj: UpdateBookSchema, response: Response,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Book).where(Book.id == book_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            update_values = obj.model_dump(exclude_unset=True)
            if not update_values:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorSchema(error="No fields to update")
            try:
                stmt = update(Book).where(
                    Book.id == book_id
                ).values(**update_values)
                await session.execute(statement=stmt)
                await session.commit()
                return ResponseSchema(
                    response=f"Book {book_id} is updated!"
                )
            except Exception as e:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorSchema(error=str(e))
            
        return Response(status_code=status.HTTP_404_NOT_FOUND)
        

books = Books()
