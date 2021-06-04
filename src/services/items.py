from src.util.logging import get_logger
from src.database.repos.item_repo import ItemRepo
from fastapi import Depends
from src.util.logging import get_logger
from src.models.item import ItemTemplate, Item, ItemUpdate

logger = get_logger(__name__)

class ItemsService():
    def __init__(
        self,
        item_repo: ItemRepo = Depends()
    ) -> None:
        self.item_repo = item_repo
    
    async def get_items(self):
        items = await self.item_repo.get_items()
        return items
    
    async def create_item(self, item_template: ItemTemplate) -> Item:
        created_item = await self.item_repo.create_item(item_template)
        return created_item
    
    async def update_item(self, name: str, item_update: ItemUpdate) -> Item:
        updated_item = await self.item_repo.update_item(name, item_update)
        return updated_item