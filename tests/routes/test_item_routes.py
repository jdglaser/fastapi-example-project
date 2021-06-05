import asyncio
from src.util.logging import get_logger
from src.models.item import ItemTemplate
import pytest
from httpx import AsyncClient
from fastapi import FastAPI, status

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

    @pytest.mark.asyncio
    async def test_get_item_failure(self):
        print("getting items the first time")
        res = await self.client.get("/items/")
        print(res)
        print(res.content)
        print("Sleeping for 2 minutes before trying")
        print("getting items the second time")
        await asyncio.sleep(90)
        res = await self.client.get("/items/")
        print(res)
        print(res.content)
        assert res[0].name == "foo"
        assert res[0].description == "bar"
        assert 1 == 2 
    
