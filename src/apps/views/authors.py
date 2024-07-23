# FastApi
from fastapi import (
    Depends, APIRouter, Response, status, Form, UploadFile, File
)

# Thirt-Party
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from PIL import Image

# Python
from typing import Annotated, Optional
import os
import io

# Local
from src.settings.const import VOLUME
from src.apps.utils.session import get_async_session
from src.apps.models.authors import Author
from src.apps.schemas.authors import (
    AuthorSchema, AllAuthorsSchema, CreateAuthorSchema,
)
from src.apps.schemas.response import ResponseSchema, ErrorSchema


class Authors:
    """View for Authors."""

    def __init__(self) -> None:
        self.path = "/authors"
        self.router = APIRouter(
            prefix="/api/v1", tags=["Authors CRUD"]
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.create_author, 
            methods=["POST"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema}
            }
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.get_all_authors, 
            description="""Get all authors with pagination,
            pages begining by 0""",
            methods=["GET"], responses={
                200: {"model": AllAuthorsSchema},
                204: {"model": None}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{author_id}", endpoint=self.update_author, 
            methods=["PUT"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema},
                404: {"model": None}
            }
        )
        self.router.add_api_route(
            path=self.path+"/{author_id}", endpoint=self.remove_author, 
            methods=["DELETE"], responses={
                200: {"model": ResponseSchema},
                404: {"model": None}
            }
        )

    async def create_author(
        self, first_name: Annotated[str, Form()], response: Response,
        last_name: Annotated[str, Form()], avatar: UploadFile = None,
        session: AsyncSession = Depends(get_async_session)
    ):
        try:
            data = CreateAuthorSchema(
                first_name=first_name, last_name=last_name, avatar=avatar
            )
            query = insert(Author).values(
                first_name=data.first_name, last_name=data.last_name,
                avatar=data.avatar
            )
            await session.execute(query)
            await session.commit()
            return ResponseSchema(
                response=f"Author {data.first_name} {data.last_name} is created!"
            )
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorSchema(error=str(e))

    async def get_all_authors(
        self, page_number: int = 0, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Author).limit(50).offset(page_number)
        temp = await session.execute(query)
        data = temp.scalars().all()
        if not data:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        obj = []
        for item in data:
            obj.append(AuthorSchema(
                id=item.id, first_name=item.first_name, 
                last_name=item.last_name, avatar=item.avatar
            ))
        result = AllAuthorsSchema(response=obj)
        return result
    
    async def update_author(
        self, author_id: int, response: Response,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        avatar: Optional[UploadFile] = File(None), 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Author).where(Author.id == author_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            update_values = {}
            if first_name:
                update_values['first_name'] = first_name
            if last_name:
                update_values['last_name'] = last_name
            if avatar:
                image = Image.open(io.BytesIO(await avatar.read()))
                name = os.urandom(32).hex()
                avatar_filename = f"authors/{name}"
                avatar_path = os.path.join(VOLUME, avatar_filename)
                os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
                update_values['avatar'] = avatar_path
                image.save(avatar_path)
            if not update_values:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorSchema(error="No fields to update")

            try:
                stmt = update(Author).where(
                    Author.id == author_id
                ).values(**update_values)
                await session.execute(statement=stmt)
                await session.commit()
                return ResponseSchema(
                    response=f"Author {author_id} is updated!"
                )
            except Exception as e:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorSchema(error=str(e))
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    async def remove_author(
        self, author_id: int,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Author).where(Author.id == author_id)
        temp = await session.execute(query)
        data = temp.scalar()
        if data:
            stmt = delete(Author).where(Author.id == author_id)
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(
                response=f"Author {author_id} is removed!"
            )
        return Response(status_code=status.HTTP_404_NOT_FOUND)


authors = Authors()
