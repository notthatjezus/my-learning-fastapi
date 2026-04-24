# dao.py(Data Access Object) можно назвать service.py или repo.py

from datetime import date
from operator import and_, or_
import select

from sqlalchemy import delete, insert, select, func

from app.database import async_session_maker, engine
from app.dao.base import BaseDAO

from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms

class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND
            (date_from >= '2023-10-01' AND date_from <= '2023-11-01') OR
            (date_from <= '2023-10-01' AND date_to > '2023-10-01')
        )
        SELECT rooms.quanity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quanity, booked_rooms.room_id
        """
        async with async_session_maker() as session:
            booked_rooms = select(Bookings).where(
                and_(
                    Bookings.room_id == room_id,
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from
                        )
                    )
                )
            ).cte("booked_rooms")

            get_rooms_left = select(
                (Rooms.quanity - func.count(booked_rooms.c.room_id)).label("rooms_left")
                ).select_from(Rooms).outerjoin(
                    booked_rooms, booked_rooms.c.room_id == Rooms.id
                ).where(Rooms.id == room_id).group_by(Rooms.quanity, booked_rooms.c.room_id)

            print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))

            rooms_left = await session.execute(get_rooms_left)

            rooms_left = rooms_left.scalar()
            print(rooms_left)

            if rooms_left is None:
                rooms_left = 0

            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()

                add_booking = insert(Bookings).values(
                    room_id=room_id,
                    user_id=user_id,
                    date_from=date_from,
                    date_to=date_to,
                    price=price,
                ).returning(Bookings)

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.scalar()

            else:
                return None


    @classmethod
    async def delete_booking(
        cls,
        user_id: int
    ):
        async with async_session_maker() as session:
            query = delete(Bookings).where(Bookings.user_id==user_id)

            await session.execute(query)
            await session.commit()
            return {"status": "success"}