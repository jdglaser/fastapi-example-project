from src.util.logging import get_logger
from src.models.item import ItemTemplate
import pytest
from httpx import AsyncClient
from fastapi import FastAPI, status

class TestItemRoutes:
    @pytest.mark.asyncio
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post("/items/", json=ItemTemplate(name="baz", description="soap").dict())
        assert res.status_code == status.HTTP_200_OK
    
