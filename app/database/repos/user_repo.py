from datetime import datetime
from typing import Optional, Tuple

from app.database.database import db
from app.database.tables.user import user_table
from app.models.user import AuthUser, AuthUserTemplate, User
from app.util.helpers import remove_from_dict
from app.util.logging import get_logger
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status

LOG = get_logger(__name__)

async def get_auth_user(username: str) -> AuthUser:
    LOG.info(f"Getting user {username} with auth information")
    async with db.transaction():
        stmt = user_table.select().where(user_table.c.username == username)
        res = await db.fetch_one(stmt)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User {username} not found.")
        return AuthUser(**dict(res))

async def create_user(user: AuthUserTemplate) -> User:
    username = user.username
    LOG.info(f"Creating user {username}")
    async with db.transaction():
        stmt = user_table.insert().returning(user_table)
        try:
            res = await db.fetch_one(query=stmt, values=remove_from_dict(dict(user), "password"))
            return User(**dict(res))
        except UniqueViolationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with name {username} already exists."
            )

async def get_user_refresh_token(username: str) -> Tuple[Optional[str], Optional[datetime]]:
    user = await get_auth_user(username)
    return (user.refresh_token, user.refresh_token_expires_at)

async def update_user_refresh_token(username: str, new_token: str, new_token_expiry: datetime) -> None:
    async with db.transaction():
        stmt = (
            user_table.update()
                .where(user_table.c.username == username)
                .values(refresh_token=new_token, refresh_token_expires_at=new_token_expiry)
                .returning(user_table)
        )
        res = await db.fetch_one(query=stmt)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )
        