from pydantic import BaseModel, ConfigDict


class SRooms(BaseModel):

    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: list[str]
    quanity: int
    image_id: int

    model_config = ConfigDict(from_attributes=True)


class SRoomsEdit(BaseModel):

    name: str
    description: str
    price: int
    services: list[str]
    quanity: int
    image_id: int | None = None

    model_config = ConfigDict(from_attributes=True)