from databases import Database
from app.config import settings
from sqlalchemy import MetaData
from app.util.logging import get_logger
from fastapi import FastAPI, Request, Depends
from app.database.repos.base_repo import BaseRepo
from typing import Type, Callable

logger = get_logger(__name__)

DATABASE_URL: str = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
METADATA = MetaData()

def get_database(request: Request) -> Database:
    return request.app.state._db

def get_repository(repo_type: Type[BaseRepo]) -> Callable:
    def get_repo(db: Database = Depends(get_database)) -> BaseRepo:
        return repo_type(db)
    return get_repo

async def connect_to_db(app: FastAPI) -> None:
    logger.info("Connecting to database")
    database = Database(DATABASE_URL, 
                        min_size=settings.db_min_connection_pool_size, 
                        max_size=settings.db_max_connection_pool_size)
    try:
        await database.connect()
        app.state._db = database
        logger.info("Connected to database")
    except Exception as e:
        logger.warn("--- DB CONNECTION ERROR ---")
        logger.warn(e)
        logger.warn("--- DB CONNECTION ERROR ---")

async def close_db_connection(app: FastAPI) -> None:
    logger.info("Disconnecting from database")
    try:
        await app.state._db.disconnect()
        logger.info("Disconnected from database")
    except Exception as e:
        logger.warn("--- DB DISCONNECT ERROR ---")
        logger.warn(e)
        logger.warn("--- DB DISCONNECT ERROR ---")
