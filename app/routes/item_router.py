from app.util.cbv import cbv
from app.models.item import Item, ItemTemplate, ItemUpdate
from fastapi import APIRouter, Depends
from app.database.repos.item_repo import ItemRepo
from app.database.database import get_repo
from app.services.items import ItemsService
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(
        prefix="/items",
        tags=["items"],
        #dependencies=[Depends(verify_current_user)],
        responses={404: {"description": "Not found"}},
    )

@cbv(router)
class ItemRouter():
    auth_service = Depends(AuthService)
    item_service = Depends(ItemsService)
    user_service: UserService = Depends(UserService)

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
