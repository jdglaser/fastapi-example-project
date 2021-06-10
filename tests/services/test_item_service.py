import pytest
from src.database.repos.item_repo import ItemRepo
from src.models.item_models import ItemTemplate
from src.services.item_service import ItemService


@pytest.fixture(scope="class", autouse=True)
def get_item_service(request, db) -> ItemService:
    item_repo = ItemRepo(db)
    request.cls.item_service = ItemService(item_repo)

@pytest.mark.usefixtures("get_item_service")
class TestItemService:
    item_service: ItemService

    foo_item = ItemTemplate(name="foo", description="bar")
    @pytest.mark.asyncio
    async def test_create_item(self):
        res = await self.item_service.create_item(self.foo_item)
        assert res.name == "foo"
        assert res.description == "bar"
    
    @pytest.mark.asyncio
    async def test_get_item(self):
        res = await self.item_service.get_items()
        assert res[0].name == "foo"
        assert res[0].description == "bar"

