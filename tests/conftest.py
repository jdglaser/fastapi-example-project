from datetime import date, datetime

import json
from src.database.database import close_db_connection, connect_to_db
from src.models.user import AuthUserTemplate, User, UserTemplate
import warnings
import os

import pytest
from asgi_lifespan import LifespanManager
from typing import AsyncGenerator, Generator

from fastapi import FastAPI
from httpx import AsyncClient
from databases import Database
from fastapi.encoders import jsonable_encoder
import alembic
from alembic.config import Config
import asyncio
from src.config import Settings, get_settings

@pytest.fixture(scope="class")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

# Apply migrations at beginning of each test class
@pytest.fixture(scope="class", autouse=True)
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")

    alembic.command.downgrade(config, "base")
    alembic.command.upgrade(config, "head")
    yield

@pytest.fixture(scope="class")
def settings():
    return get_settings()


# Create a new application for testing
@pytest.fixture(scope="class")
async def app(apply_migrations: None, settings: Settings) -> AsyncGenerator[FastAPI, None]:
    from src.main import get_application

    settings.access_token_expire_minutes = 500

    app = get_application()
    print(os.getenv("TESTING"))
    if os.getenv("TESTING"):
        print("TESTING!")
    else:
        print("NOT TESTING")
    await connect_to_db(app)
    yield app
    await close_db_connection(app)


# Grab a reference to our database when needed
@pytest.fixture(scope="class")
def db(app: FastAPI) -> Database:
    return app.state.db

@pytest.fixture(scope="class")
def test_user() -> UserTemplate:
    return UserTemplate(username="johndoe", 
                        email="johndoe@gmail.com",
                        first_name="John",
                        last_name="Doe",
                        date_of_birth=date(1992, 3, 21),
                        password="12345")

# Make requests in our tests
@pytest.fixture(scope="class")
async def client(app: FastAPI, test_user: UserTemplate, settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    print("EXPIRES IN: ", settings.access_token_expire_minutes)
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"}
    ) as client:
        await client.post("/auth/", json=jsonable_encoder(test_user))
        res = await client.post("/auth/login/", params={"username": test_user.username, "password": test_user.password})
        token = res.json()["accessToken"]
        token_type = res.json()["tokenType"]
        client.headers["Authorization"] = f"{token_type} {token}"
        yield client
