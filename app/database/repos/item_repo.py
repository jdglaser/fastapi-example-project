from app.database.database import db
from app.database.tables.item import item_table
from app.models.item import Item, ItemTemplate, ItemUpdate
from app.util.logging import get_logger
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException

logger = get_logger(__name__)

async def get_items() -> list[Item]:
    logger.info("Getting items")
    async with db.transaction():
        stmt = item_table.select()
        res = await db.fetch_all(query=stmt)
        return [Item(**dict(r)) for r in res]

async def create_item(item: ItemTemplate) -> Item:
    async with db.transaction():
        stmt = (
            item_table.insert()
                .returning(item_table)
        )
        try:
            res = await db.fetch_all(query=stmt, values=dict(item))
        except UniqueViolationError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Item with name {item.name} already exists."
            )
        return Item(**[dict(r) for r in res][0])

async def update_item(name: str, item: ItemUpdate) -> Item:
    async with db.transaction():
        stmt = (
            item_table.update()
                .where(item_table.c.name == name)
                .values(dict(item))
                .returning(item_table)
        )
        res = await db.fetch_all(query=stmt)
        if (len(res) == 0):
            raise HTTPException(
                status_code=404,
                detail=f"Item {name} does not exist"
            )
        return Item(**[dict(r) for r in res][0])


