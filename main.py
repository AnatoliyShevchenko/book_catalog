# Third-Party
import uvicorn
import asyncio

# Local
from src.settings.base import app, logger, AIOREDIS


async def main():
    app.include_router(router=...)
    config = uvicorn.Config(
        app="main:app", host="0.0.0.0", port=8040
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
