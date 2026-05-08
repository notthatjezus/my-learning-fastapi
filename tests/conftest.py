import asyncio
import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert, text

from app.bookings.models import Bookings
from app.config import settings
from app.database import Base, async_session_maker, engine
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.main import app as fastapi_app
from app.users.models import Users


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r") as file:
            return json.load(file)


    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    users = open_mock_json("users")
    bookings = open_mock_json("bookings")

    for booking in bookings:
            booking["date_from"] = datetime.strptime(booking["date_from"], "%Y-%m-%d")
            booking["date_to"] = datetime.strptime(booking["date_to"], "%Y-%m-%d")


    async with async_session_maker() as session:
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms)
        add_users = insert(Users).values(users)
        add_bookings = insert(Bookings).values(bookings)

        await session.execute(add_hotels)
        await session.execute(add_rooms)
        await session.execute(add_users)
        await session.execute(add_bookings)

        await session.commit()

        # Сбрасываем счетчики ID для всех таблиц
        for table in ["hotels", "rooms", "users", "bookings"]:
            await session.execute(
                text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1)) FROM {table}")
            )
        await session.commit()



# Взято из документации pytest
@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def ac(): # asyncclient
     transport = ASGITransport(app=fastapi_app)
     async with AsyncClient(transport=transport, base_url="http://test") as ac:
          yield ac

    
@pytest.fixture(scope="session")
async def authenticated_ac(): # asyncclient
     transport = ASGITransport(app=fastapi_app)
     async with AsyncClient(transport=transport, base_url="http://test") as ac:
          await ac.post("/auth/login", json={
               "email": "test@test.com",
               "password": "$6$rounds=656000$xyz...test_hash"
          })
          assert ac.cookies["booking_access_token"]
          yield ac


@pytest.fixture(scope="function")
async def session():
     async with async_session_maker() as session:
          yield session


