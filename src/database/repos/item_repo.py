from typing import Optional
from sqlalchemy.sql.elements import and_, literal_column
from starlette.status import HTTP_404_NOT_FOUND
from src.models.user_models import User
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from src.database.repos.base_repo import BaseRepo
from src.database.tables.item_tables import item_table
from src.models.item_models import Item, ItemTemplate, ItemUpdate
from src.util.logging import get_logger

logger = get_logger(__name__)

class ItemRepo(BaseRepo):
    async def get_items(self, user: User) -> list[Item]:
        async with self.db.transaction():
            stmt = item_table.select().where(item_table.c.user_id == user.id)
            res = await self.db.fetch_all(query=stmt)
            return [Item(**r) for r in res]

    async def create_item(self, item: ItemTemplate, user_id: int) -> Item:
        async with self.db.transaction():
            stmt = (
                item_table.insert()
                    .returning(item_table)
            )
            try:
                res = await self.db.fetch_one(query=stmt, values={**item.dict(), "user_id": user_id})
            except UniqueViolationError as e:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Item with name {item.name} already exists."
                )
            if not res:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to insert item {item.name}"
                )
            return Item(**res)

    async def update_item(self, name: str, item: ItemUpdate, user_id: int) -> Item:
        async with self.db.transaction():
            stmt = (
                item_table.update()
                    .where(
                        and_(
                            item_table.c.name == name,
                            item_table.c.user_id == user_id
                        )
                    )
                    .values({**item.dict()})
                    .returning(item_table)
            )
            res = await self.db.fetch_one(query=stmt)
            if not res:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item {name} does not exist for user {user_id}"
                )
            return Item(**res)
        
    async def delete_item(self, item_id: int, user_id: int) -> Item:
        async with self.db.transaction():
            stmt = (
                item_table.delete()
                    .where(
                        and_(
                            item_table.c.id == item_id,
                            item_table.c.user_id == user_id
                        )
                    )
                    .returning(*item_table.columns)
            )
            res = await self.db.fetch_one(query=stmt)
            if not res:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail=f"Failed to delete item with id {item_id} for user {user_id}"
                )
            return Item(**res)


