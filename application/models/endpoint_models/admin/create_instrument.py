from pydantic import BaseModel, Field


class CreateInstrumentRequest(BaseModel):
    name: str
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
