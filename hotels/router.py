

import asyncio
from datetime import date

from fastapi import APIRouter, Depends

from app.exceptions import HotelsCannotBeAddedException
from app.hotels.dao import HotelsDao
from app.hotels.schemas import SHotel
from app.users.dependencies import get_current_user
from app.users.models import Users
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)

@router.get("/{location}/")
@cache(expire=30)
async def get_hotels(
    location: str,
    date_from: date,
    date_to: date
) -> list[SHotel]:
    await asyncio.sleep(3)
    return await HotelsDao.find_all(location, date_from, date_to)

@router.get("/{hotel_id}")
async def get_by_id(
    hotel_id: int
):
    return await HotelsDao.get_hotel_by_id(hotel_id)


@router.post("")
async def add_hotels(
    name: str,
    location: str,
    services: list[str],
    rooms_quantity: int,
    image_id: int,
):
    hotels = await HotelsDao.add(
        name=name,
        location=location,
        services=services,
        rooms_quantity=rooms_quantity,
        image_id=image_id
        )
    if not hotels:
        raise HotelsCannotBeAddedException


@router.patch("/{hotel_id}/")
async def edit_hotels(
    hotel_id: int,
    name: str | None = None,
    location: str | None = None,
    services: list[str] | None = None,
    rooms_quantity: int | None = None,
    image_id: int | None = None,
):
    hotel = await HotelsDao.edit(
        hotel_id=hotel_id,
        name=name,
        location=location,
        services=services,
        rooms_quantity=rooms_quantity,
        image_id=image_id
    )
    return hotel


@router.delete("/{hotel_id}")
async def delete_hotels(hotel_id: int):
    await HotelsDao.delete(hotel_id=hotel_id)
