# FastApi
from fastapi import Depends, APIRouter, Response, status

# Thirt-Party
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

# Local
from src.apps.utils.session import get_async_session
from src.apps.models.genres import Genre
from src.apps.schemas.genres import (
    GenreSchema, CreateGenreSchema, AllGenresSchema,
)
from src.apps.schemas.response import ResponseSchema, ErrorSchema


class Genres:
    """CRUD for Genres."""

    def __init__(self) -> None:
        self.path = "/genres"
        self.router = APIRouter(prefix="/api/v1", tags=["Genres CRUD"])
        self.router.add_api_route(
            path=self.path, endpoint=self.get_all_genres, 
            methods=["GET"], responses={
                200: {"model": AllGenresSchema},
                204: {"model": None}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{genre_id}", endpoint=self.get_genre,
            methods=["GET"], responses={
                200: {"model": GenreSchema},
                204: {"model": None}
            }
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.create_genre,
            methods=["POST"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{genre_id}", endpoint=self.update_genre,
            methods=["PATCH"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{genre_id}", endpoint=self.remove_genre,
            methods=["DELETE"], responses={
                200: {"model": ResponseSchema},
                404: {"model": None}
            }
        )

    async def get_all_genres(
        self, session: AsyncSession = Depends(get_async_session)
    ):
        query = sa.select(Genre)
        temp = await session.execute(query)
        data = temp.scalars().all()
        if not data:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        obj = []
        for item in data:
            obj.append(GenreSchema(id=item.id, title=item.title))
        result = AllGenresSchema(response=obj)
        return result
    
    async def get_genre(
        self, genre_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = sa.select(Genre).where(Genre.id == genre_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if not data:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        result = GenreSchema(id=data.id, title=data.title)
        return result
    
    async def create_genre(
        self, obj: CreateGenreSchema, response: Response,
        session: AsyncSession = Depends(get_async_session)
    ):
        try:
            stmt = sa.insert(Genre).values(title=obj.title)
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(
                response=f"Genre {obj.title} is created!"
            )
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorSchema(error=str(e))
        
    async def update_genre(
        self, genre_id: int, obj: CreateGenreSchema, response: Response,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = sa.select(Genre).where(Genre.id == genre_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            try:
                stmt = sa.update(Genre).where(
                    Genre.id == genre_id
                ).values(title=obj.title)
                await session.execute(statement=stmt)
                await session.commit()
                return ResponseSchema(
                    response=f"Genre {genre_id} is updated!"
                )
            except Exception as e:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorSchema(error=str(e))
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    async def remove_genre(
        self, genre_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = sa.select(Genre).where(Genre.id == genre_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            stmt = sa.delete(Genre).where(Genre.id == genre_id)
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(
                response=f"Genre {genre_id} is removed!"
            )
        return Response(status_code=status.HTTP_404_NOT_FOUND)


genres = Genres()
