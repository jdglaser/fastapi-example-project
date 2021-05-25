import databases
from app.config import settings
from sqlalchemy import MetaData

db_url: str = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
db = databases.Database(db_url,
                        ssl=False,
                        min_size=settings.db_min_connection_pool_size,
                        max_size=settings.db_max_connection_pool_size)

metadata = MetaData()
