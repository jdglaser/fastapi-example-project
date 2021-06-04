from src.database.database import METADATA
from src.database.tables.common_columns import get_common_columns
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Table
from sqlalchemy.sql import text

user_table = Table(
    "user",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False, unique=True),
    Column("email", String, nullable=False, unique=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=True),
    Column("date_of_birth", Date, nullable=False),
    Column("disabled", Boolean, nullable=False, server_default=text("FALSE")),
    Column("hashed_password", String, nullable=False),
    Column("refresh_token", String, nullable=True),
    Column("refresh_token_expires_at", DateTime, nullable=True),
    *get_common_columns()
)
