from datetime import datetime
from typing import Optional, Tuple

from src.database.tables.user import user_table
from src.models.user import AuthUser, AuthUserTemplate, User
from src.util.helpers import remove_from_dict
from src.util.logging import get_logger
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from src.database.repos.base_repo import BaseRepo

logger = get_logger(__name__)

class UserRepo(BaseRepo):
    async def find_user(self, username: str) -> Optional[User]:
        logger.info(f"Finding user {username}")
        async with self.db.transaction():
            stmt = user_table.select().where(user_table.c.username == username)
            res = await self.db.fetch_one(stmt)
            if res:
                return User(**res)
            return None
    
    async def find_user_by_email(self, email: str) -> Optional[User]:
        logger.info(f"Finding user by email {email}")
        async with self.db.transaction():
            stmt = user_table.select().where(user_table.c.email == email)
            res = await self.db.fetch_one(stmt)
            if res:
                return User(**res)
            return None
    
    async def find_user_by_refresh_token(self, refresh_token: str) -> Optional[User]:
        async with self.db.transaction():
            stmt = user_table.select().where(user_table.c.refresh_token == refresh_token)
            res = await self.db.fetch_one(stmt)
            if res:
                return User(**res)
            return None

    async def get_auth_user(self, username: str) -> AuthUser:
        logger.info(f"Getting user {username} with auth information")
        async with self.db.transaction():
            stmt = user_table.select().where(user_table.c.username == username)
            res = await self.db.fetch_one(stmt)
            if not res:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"User {username} not found.")
            return AuthUser(**dict(res))

    async def create_user(self, user: AuthUserTemplate) -> User:
        username = user.username
        logger.info(f"Creating user {username}")
        async with self.db.transaction():
            stmt = user_table.insert().returning(user_table)
            res = await self.db.fetch_one(query=stmt, values=remove_from_dict(user.dict(), "password"))
            if not res:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to insert user {username}"
                )
            return User(**res)

    async def get_user_refresh_token(self, username: str) -> Tuple[Optional[str], Optional[datetime]]:
        user = await self.get_auth_user(username)
        return (user.refresh_token, user.refresh_token_expires_at)

    async def update_user_refresh_token(self, username: str, new_token: str, new_token_expiry: datetime) -> None:
        async with self.db.transaction():
            stmt = (
                user_table.update()
                    .where(user_table.c.username == username)
                    .values(refresh_token=new_token, refresh_token_expires_at=new_token_expiry)
                    .returning(user_table)
            )
            res = await self.db.fetch_one(query=stmt)
            if not res:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {username} not found"
                )
            