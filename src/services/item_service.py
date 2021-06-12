from src.models.user_models import User
from src.services.auth_service import AuthService
from src.util.logging import get_logger
from src.database.repos.item_repo import ItemRepo
from fastapi import Depends
from src.util.logging import get_logger
from src.models.item_models import ItemTemplate, Item, ItemUpdate

logger = get_logger(__name__)

class ItemService():
    get_current_user = AuthService.get_current_user

    def __init__(
        self,
        item_repo: ItemRepo = Depends(),
        current_user: User = Depends(get_current_user)
    ) -> None:
        self.item_repo = item_repo
        self.current_user = current_user
    
    async def get_items(self):
        items = await self.item_repo.get_items(self.current_user)
        return items
    
    async def create_item(self, item_template: ItemTemplate) -> Item:
        created_item = await self.item_repo.create_item(item_template, self.current_user.id)
        return created_item
    
    async def update_item(self, name: str, item_update: ItemUpdate) -> Item:
        updated_item = await self.item_repo.update_item(name, item_update, self.current_user.id)
        return updated_item

    async def delete_item(self, item_id: int) -> Item:
        return await self.item_repo.delete_item(item_id, self.current_user.id)