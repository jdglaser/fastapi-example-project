import os
from databases import Database
from src.config import settings
from sqlalchemy import MetaData
from src.util.logging import get_logger
from fastapi import FastAPI, Request, Depends
from src.database.repos.base_repo import BaseRepo
from typing import Type, Callable

logger = get_logger(__name__)

port = settings.db_port_test if os.environ.get("TESTING") else settings.db_port
DATABASE_URL: str = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{port}/{settings.db_name}"
METADATA = MetaData()

async def connect_to_db(app: FastAPI) -> None:
    logger.info("Connecting to database")
    database = Database(DATABASE_URL, 
                        min_size=settings.db_min_connection_pool_size, 
                        max_size=settings.db_max_connection_pool_size)
    try:
        await database.connect()
        app.state.db = database
        logger.info("Connected to database")
    except Exception as e:
        logger.warn("--- DB CONNECTION ERROR ---")
        logger.warn(e)
        logger.warn("--- DB CONNECTION ERROR ---")

async def close_db_connection(app: FastAPI) -> None:
    logger.info("Disconnecting from database")
    try:
        await app.state.db.disconnect()
        logger.info("Disconnected from database")
    except Exception as e:
        logger.warn("--- DB DISCONNECT ERROR ---")
        logger.warn(e)
        logger.warn("--- DB DISCONNECT ERROR ---")