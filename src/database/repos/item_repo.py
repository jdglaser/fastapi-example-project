from src.database.tables.item import item_table
from src.models.item import Item, ItemTemplate, ItemUpdate
from src.util.logging import get_logger
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException
from src.database.repos.base_repo import BaseRepo
from fastapi import status

logger = get_logger(__name__)

class ItemRepo(BaseRepo):
    async def get_items(self) -> list[Item]:
        logger.info("Getting items")
        async with self.db.transaction():
            stmt = item_table.select()
            res = await self.db.fetch_all(query=stmt)
            return [Item(**r) for r in res]

    async def create_item(self, item: ItemTemplate) -> Item:
        async with self.db.transaction():
            stmt = (
                item_table.insert()
                    .returning(item_table)
            )
            try:
                res = await self.db.fetch_one(query=stmt, values=dict(item))
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

    async def update_item(self, name: str, item: ItemUpdate) -> Item:
        async with self.db.transaction():
            stmt = (
                item_table.update()
                    .where(item_table.c.name == name)
                    .values(dict(item))
                    .returning(item_table)
            )
            res = await self.db.fetch_one(query=stmt)
            if not res:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item {name} does not exist"
                )
            return Item(**res)
        
    async def delete_item(self, item_id: int) -> None:
        async with self.db.transaction():
            stmt = (
                item_table.delete()
                    .where(item_table.c.id == item_id)
            )
            await self.db.execute(query=stmt)


