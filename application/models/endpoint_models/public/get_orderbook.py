from pydantic import BaseModel, Field


class LevelResponse(BaseModel):
    price: int
    qty: int


class GetOrderbookResponse(BaseModel):
    bid_levels: list[LevelResponse]
    ask_levels: list[LevelResponse]
