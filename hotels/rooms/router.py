from datetime import date

from fastapi import APIRouter

from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRoomsEdit


router = APIRouter(
    prefix="/hotels",
    tags=["Номера отелей"]
)

@router.get("/{hotel_id}/rooms")
async def find_free_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date
):
    return await RoomDAO.find_all(hotel_id, date_from, date_to)

@router.post("/{hotel_id}/rooms")
async def add_rooms(
    hotel_id: int,
    room_data: SRoomsEdit
):
    return await RoomDAO.add(
        hotel_id,
        **room_data.model_dump()
    )


@router.patch("/{hotel_id}/rooms/{room_id}")
async def edit_rooms(
    hotel_id: int,
    room_id: int,
    room_data: SRoomsEdit
):
    return await RoomDAO.edit(
        room_id,
        **room_data.model_dump()
    )


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
    hotel_id: int,
    room_id: int
):
    return await RoomDAO.delete(
        room_id
    )