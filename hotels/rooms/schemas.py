from pydantic import BaseModel


class SRooms(BaseModel):

    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: list[str]
    quanity: int
    image_id: int

    class Config:
        from_attributes = True


class SRoomsEdit(BaseModel):

    name: str
    description: str
    price: int
    services: list[str]
    quanity: int
    image_id: int | None = None

    class Config:
        from_attributes = True