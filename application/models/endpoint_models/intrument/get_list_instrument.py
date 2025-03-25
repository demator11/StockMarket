from pydantic import BaseModel


class InstrumentListResponse(BaseModel):
    name: str
    ticker: str
