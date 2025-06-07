from pydantic import BaseModel


class Level(BaseModel):
    price: int
    qty: int


class GetOrderbookResponse(BaseModel):
    bid_levels: list[Level]
    ask_levels: list[Level]
