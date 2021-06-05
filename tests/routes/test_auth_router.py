from datetime import date

from starlette.status import HTTP_200_OK
from src.models.user import UserTemplate
import pytest
from httpx import AsyncClient
from fastapi.encoders import jsonable_encoder
from fastapi import status

@pytest.fixture(scope="function")
def setup(request, client: AsyncClient):
    request.cls.client = client
    request.cls.client.headers.pop("Authorization", None)

@pytest.mark.usefixtures("setup")
class TestAuthService:
    client: AsyncClient

    new_test_user = UserTemplate(username="johndoe2", 
                             email="johndoe2@gmail.com",
                             first_name="John",
                             last_name="Doe",
                             date_of_birth=date(1992, 3, 21),
                             password="12345")

    @pytest.mark.asyncio
    async def test_create_new_user(self):
        res = await self.client.post("/auth/", json=jsonable_encoder(self.new_test_user))
        assert res.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_sign_in_user(self):
        await self.client.post("/auth/", json=jsonable_encoder(self.new_test_user))
        res = await self.client.post("/auth/login/", params={"username": "johndoe", "password": "12345"})
        data = res.json()
        assert res.status_code == HTTP_200_OK
        assert "accessToken" in data
        assert "tokenType" in data
        assert data["tokenType"] == "bearer"

