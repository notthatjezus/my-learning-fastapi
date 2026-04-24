from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis
from sqladmin import Admin, ModelView

import uvicorn

from typing import Optional
from datetime import date
from pydantic import BaseModel

from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.admin.auth import authentication_backend
from app.config import settings
from app.database import engine

from app.users.models import Users
from app.users.router import router as router_users
from app.bookings.router import router as router_bookings
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms

from app.pages.router import router as router_pages
from app.images.router import router as router_images


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация Redis при старте
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi_cache")
    yield
    # Закрываем соединение при выключении
    await redis.close()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_rooms)

app.include_router(router_pages)
app.include_router(router_images)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin", "Authorization"]

)


admin = Admin(app, engine, authentication_backend=authentication_backend)


admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)


# class HotelsSearchArgs:
#     def __init__(
#             self,
#             location: str,
#             date_from,
#             date_to,
#             has_spa: Optional[bool] = None,
#             stars: Optional[int] = Query(None, ge=1, le=5)
#     ):
#             self.location = location
#             self.date_from = date_from
#             self.date_to = date_to
#             self.has_spa = has_spa
#             self.stars = stars


# class SchemaHotel(BaseModel):
#     address: str
#     name: str
#     stars: int


# @app.get("/hotels")#response_model=list[SchemaHotel])
# def get_hotels(
#      search_args: HotelsSearchArgs = Depends()
# ):
#     return search_args


# @app.get("/hotels/")#response_model=list[SchemaHotel])
# def get_hotels(
#     location: str,
#     date_from,
#     date_to,
#     has_spa: Optional[bool] = None,
#     stars: Optional[int] = Query(None, ge=1, le=5)
# ) -> list[SchemaHotel]:
#     hotels = [
#         {
#             "address": "st. Gagarina, 1, Moscow",
#             "name": "Super Hotel",
#             "stars": 5,
#         },
#         {
#             "address": "st. Gagarina, 5, Moscow",
#             "name": "NOSuper Hotel",
#             "stars": 4,
#         },
#     ]
#     return hotels



if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)