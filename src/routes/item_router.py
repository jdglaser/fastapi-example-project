from src.util.cbv import cbv
from src.models.item import Item, ItemTemplate, ItemUpdate
from fastapi import APIRouter, Depends
from src.services.items import ItemsService
from src.services.auth import AuthService
import asyncio

router = APIRouter(
        prefix="/items",
        tags=["items"],
        responses={404: {"description": "Not found"}},
    )

@cbv(router)
class ItemRouter():
    username: str = Depends(AuthService.verify_current_user)
    item_service: ItemsService = Depends()

    @router.get("/", response_model=list[Item])
    async def get_items(self) -> list[Item]:
        items = await self.item_service.get_items()
        return items

    @router.post("/")
    async def create_item(self, item_template: ItemTemplate) -> Item:
        return await self.item_service.create_item(item_template)

    @router.put("/")
    async def update_item(self, name: str, 
                        item: ItemUpdate) -> Item:
        return await self.item_service.update_item(name, item)
    
    @router.delete("/{item_id}")
    async def delete_item(self, item_id: int) -> None:
        return await self.item_service.delete_item(item_id)
