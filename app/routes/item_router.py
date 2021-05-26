from app.models.item import Item, ItemTemplate, ItemUpdate
from app.util.auth import verify_current_user
from fastapi import APIRouter, Depends
from app.database.repos.item_repo import ItemRepo
from app.database.database import get_repository

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(verify_current_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[Item])
async def get_items(item_repo: ItemRepo = Depends(get_repository(ItemRepo))) -> list[Item]:
    items = await item_repo.get_items()
    return items

@router.post("/")
async def create_item(item: ItemTemplate,
                      item_repo: ItemRepo = Depends(get_repository(ItemRepo))):
    return await item_repo.create_item(item)

@router.put("/")
async def update_item(name: str, 
                      item: ItemUpdate,
                      item_repo: ItemRepo = Depends(get_repository(ItemRepo))):
    return await item_repo.update_item(name, item)
