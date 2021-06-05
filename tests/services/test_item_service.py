from src.database.repos.item_repo import ItemRepo
from src.models.item import ItemTemplate
from src.services.items import ItemsService
import pytest

@pytest.fixture(scope="class", autouse=True)
def item_service(db) -> ItemsService:
    item_repo = ItemRepo(db)
    return ItemsService(item_repo)

class TestItemService:
    @pytest.mark.asyncio
    async def test_create_item(self, item_service: ItemsService):
        res = await item_service.create_item(ItemTemplate(name="foo", description="bar"))
        assert res.name == "foo"
        assert res.description == "bar"
    
    @pytest.mark.asyncio
    async def test_create_another_item(self, item_service: ItemsService):
        res = await item_service.create_item(ItemTemplate(name="pow", description="mow"))
        assert res.name == "pow"
        assert res.description == "mow"

