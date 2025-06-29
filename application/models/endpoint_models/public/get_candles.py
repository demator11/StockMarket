from datetime import datetime

from pydantic import BaseModel


class CandleStick(BaseModel):
    open_price: int
    high_price: int
    low_price: int
    close_price: int
    volume: int
    timestamp: datetime


class GetCandlesResponse(BaseModel):
    ticker: str
    candles: list[CandleStick]
