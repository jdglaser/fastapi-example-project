import pytest
from fastapi import status
from httpx import AsyncClient
from src.models.item_models import ItemTemplate
from src.util.logging import get_logger


@pytest.fixture(scope="class")
def setup(request, client: AsyncClient):
    request.cls.client = client

@pytest.mark.usefixtures("setup")
class TestItemRoutes:
    client: AsyncClient
    @pytest.mark.asyncio
    async def test_routes_exist(self) -> None:
        res = await self.client.post("/items/", json=ItemTemplate(name="baz", description="soap").dict())
        assert res.status_code == status.HTTP_200_OK
