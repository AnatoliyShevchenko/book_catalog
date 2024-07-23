# Third-Party
import click
from sqlalchemy.future import select

# Local
from src.settings.base import fake, session
from src.apps.models import Author, Genre, Book


async def create_fake_records():
    async with session() as conn:
        authors = []
        genres = []

        for _ in range(10):
            author = Author(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            conn.add(author)
            authors.append(author)

        for _ in range(10):
            genre = Genre(title=fake.word())
            conn.add(genre)
            genres.append(genre)

        await conn.commit()

        authors = (await conn.execute(select(Author))).scalars().all()
        genres = (await conn.execute(select(Genre))).scalars().all()

        for _ in range(100):
            book = Book(
                title=fake.unique.sentence(nb_words=4),
                price=fake.random_int(min=10, max=100),
                pages=fake.random_int(min=100, max=1000),
                author_id=fake.random_int(min=1, max=10),
                genre_id=fake.random_int(min=1, max=10),
            )
            conn.add(book)
        
        await conn.commit()

    print("Test data inserted successfully!")

@click.command()
def cli():
    """Command Line Interface for creating fake records."""
    import asyncio
    asyncio.run(create_fake_records())

if __name__ == "__main__":
    cli()
