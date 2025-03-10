from typing import List
from pydantic import BaseModel


class L2OrderBook(BaseModel):
    class Bid(BaseModel):
        price: int
        qty: int

    class Ask(BaseModel):
        price: int
        qty: int

    bid_levels: List[Bid]
    ask_levels: List[Ask]
