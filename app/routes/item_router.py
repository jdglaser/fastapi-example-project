from app.database.repos import item_repo
from app.models.item import Item, ItemTemplate, ItemUpdate
from app.util.auth import verify_current_user
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(verify_current_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[Item])
async def get_items():
    items = await item_repo.get_items()
    return items

@router.post("/")
async def create_item(item: ItemTemplate):
    return await item_repo.create_item(item)

@router.put("/")
async def update_item(name: str, item: ItemUpdate):
    return await item_repo.update_item(name, item)
