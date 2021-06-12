from sqlalchemy import Boolean, Column, Integer, String, Table
from sqlalchemy.sql import text
from sqlalchemy.sql.schema import ForeignKey
from src.database.database import METADATA
from src.database.tables.common_columns import get_common_columns

item_table = Table(
    "item",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("name", String, nullable=False, unique=True),
    Column("description", String, nullable=False),
    Column("completed", Boolean, server_default=text("FALSE")),
    *get_common_columns()
)
