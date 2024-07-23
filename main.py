# Third-Party
import uvicorn
import asyncio

# Local
from src.settings.base import logger, AIOREDIS, app
from src.apps.views.users import reg, login_logout
from src.apps.views.genres import genres
from src.apps.views.authors import authors
from src.apps.views.books import books
from src.apps.views.reserv import reserv


async def main():
    app.include_router(router=login_logout.router)
    app.include_router(router=reg.router)
    app.include_router(router=genres.router)
    app.include_router(router=authors.router)
    app.include_router(router=books.router)
    app.include_router(router=reserv.router)
    config = uvicorn.Config(
        app="main:app", host="0.0.0.0", 
        port=8000, reload=True
    )
    server = uvicorn.Server(config=config)
    logger.info(msg="SERVER STARTED")
    await server.serve()

async def shutdown():
    await AIOREDIS.aclose()
    logger.info(msg="SHUTDOWN SERVER")

    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(shutdown())
