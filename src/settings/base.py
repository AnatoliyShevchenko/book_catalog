# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# SQL
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker,
)

# Third-Party
from redis import asyncio as aioredis

# Python
import logging
from logging.config import dictConfig

# Local
from .const import DB_URL


app = FastAPI(title="Book Catalog", debug=True)
app.add_middleware(
    middleware_class=CORSMiddleware, 
    allow_origins=["http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["GET, POST, PUT, PATCH, DELETE"],
    allow_headers=[
        "Accept", "Accept-Language", "Content-Language", "Content-Type"
    ]
)
engine = create_async_engine(url=DB_URL)
session = async_sessionmaker(
    bind=engine, expire_on_commit=True,
)
POOL = aioredis.ConnectionPool.from_url(
    url="redis://127.0.0.1:6379/7", max_connections=20
)
AIOREDIS = aioredis.Redis(connection_pool=POOL)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
        },
    },
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
dictConfig(LOGGING)
logger = logging.getLogger(__name__)
