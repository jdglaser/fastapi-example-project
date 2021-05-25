from app.database.database import metadata
from app.database.tables.common_columns import get_common_columns
from sqlalchemy import Boolean, Column, Integer, String, Table
from sqlalchemy.sql import text

item_table = Table(
    "item",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("description", String, nullable=False),
    Column("completed", Boolean, server_default=text("FALSE")),
    *get_common_columns()
)
