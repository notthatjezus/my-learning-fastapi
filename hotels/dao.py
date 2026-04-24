
from datetime import date

from sqlalchemy import and_, delete, func, insert, select, update

from app.bookings.models import Bookings
from app.database import async_session_maker, engine

from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelsDao(BaseDAO):
    model = Hotels


    @classmethod
    async def find_all(
        cls,
        location: str,
        date_from: date,
        date_to: date
    ):
        async with async_session_maker() as session:

            booked_rooms = select(
                Bookings.room_id,
                func.count(Bookings.id).label("count_booked")
            ).where(
                and_(
                    Bookings.date_from > date_from,
                    Bookings.date_to < date_to
                )
            ).group_by(Bookings.room_id).cte("booked_rooms")


            rooms_availability = (
                select(Rooms.hotel_id)
                .outerjoin(booked_rooms, Rooms.id == booked_rooms.c.room_id)
                .where((Rooms.quanity - func.coalesce(booked_rooms.c.count_booked, 0)) > 0)
            ).scalar_subquery()


            query = (
                select(Hotels)
                .where(
                    and_(
                        Hotels.id.in_(rooms_availability),
                        Hotels.location.icontains(location)
                    )
                )
            )

            print(query.compile(engine, compile_kwargs={"literal_binds": True}))

            result = await session.execute(query)
            return result.scalars().all()


    @classmethod
    async def get_hotel_by_id(
        cls,
        hotel_id: int
    ):
        async with async_session_maker() as session:
            hotel_by_id = select(Hotels).where(Hotels.id==hotel_id)

            result = await session.execute(hotel_by_id)
            return result.scalars().all()



    @classmethod
    async def add(
        cls,
        name: str,
        location: str,
        services: list[str],
        rooms_quantity: int,
        image_id: int,
    ):
        async with async_session_maker() as session:

            add_hotels = insert(Hotels).values(
                name=name,
                location=location,
                services=services,
                rooms_quantity=rooms_quantity,
                image_id=image_id
            ).returning(Hotels)

            result = await session.execute(add_hotels)
            await session.commit()
            return result.scalar()


    @classmethod
    async def edit(
        cls,
        hotel_id: int,
        **values
    ):
        async with async_session_maker() as session:
            update_data = {k: v for k, v in values.items() if v is not None}
            query = update(Hotels).where(Hotels.id==hotel_id).values(**update_data)

            await session.execute(query)
            await session.commit()


    @classmethod
    async def delete(
        cls,
        hotel_id
    ):
        async with async_session_maker() as session:
            query = delete(Hotels).where(Hotels.id==hotel_id)

        await session.execute(query)
        await session.commit()
