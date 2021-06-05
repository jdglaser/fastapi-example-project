import os
from databases import Database
from src.config import settings
from sqlalchemy import MetaData
from src.util.logging import get_logger
from fastapi import FastAPI, Request, Depends
from src.database.repos.base_repo import BaseRepo
from typing import Tuple, Type, Callable
from fastapi import Depends

logger = get_logger(__name__)

METADATA = MetaData()

def get_database_url() -> str:
    port = settings.db_port_test if os.environ.get("TESTING") else settings.db_port
    database_url: str = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{port}/{settings.db_name}"
    return database_url

async def connect_to_db(app: FastAPI) -> None:
    logger.info("Connecting to database")
    database = Database(get_database_url(), 
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
