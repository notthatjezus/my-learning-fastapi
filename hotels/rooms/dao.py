from datetime import date

from sqlalchemy import and_, delete, func, insert, select, update


from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker, engine

from app.hotels.rooms.models import Rooms


class RoomDAO(BaseDAO):
    model = Rooms


    @classmethod
    async def find_all(
        cls,
        hotel_id: int,
        date_from: date,
        date_to: date
    ):
        async with async_session_maker() as session:

            booked_rooms = select(
                 Bookings.room_id,
                 func.count(Bookings.id).label("count_booked")
            ).where(
                 and_(
                      Bookings.date_from >= date_from,
                      Bookings.date_to <= date_to
                 )
            ).group_by(Bookings.room_id).cte("booked_rooms")

            total_days = (date_to - date_from).days

            room_ava = select(
                 Rooms.__table__.columns, # Выбирает все колонки из модели Rooms
                 (Rooms.price * total_days).label("total_cost"), # Стоимость за весь период
                 (Rooms.quanity - func.coalesce(booked_rooms.c.count_booked, 0)).label("rooms_left")
            ).outerjoin(
                 booked_rooms, Rooms.id == booked_rooms.c.room_id
            ).where(
                 and_(
                      Rooms.hotel_id == hotel_id,
                      (Rooms.quanity - func.coalesce(booked_rooms.c.count_booked, 0)) > 0
                 )
            )

            result = await session.execute(room_ava)
            return result.mappings().all()


    @classmethod
    async def add(
        cls,
        hotel_id: int,
        **data
    ):
        async with async_session_maker() as session:

            add_rooms = insert(Rooms).values(
               hotel_id=hotel_id,
               **data
            ).returning(Rooms)

            result = await session.execute(add_rooms)
            await session.commit()
            return result.scalar()


    @classmethod
    async def edit(
        cls,
        room_id: int,
        **data
    ):
        async with async_session_maker() as session:

            query = update(Rooms).where(Rooms.id==room_id).values(**data)

            await session.execute(query)
            await session.commit()
            return {"status": "success"}

    @classmethod
    async def delete(
        cls,
        room_id: int
    ):
        async with async_session_maker() as session:
            query = delete(Rooms).where(Rooms.id==room_id)

            await session.execute(query)
            await session.commit()
            return {"status": "success"}