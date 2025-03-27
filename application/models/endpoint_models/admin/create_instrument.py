from pydantic import Field, BaseModel


class CreateInstrumentRequest(BaseModel):
    name: str
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
