from pydantic import BaseModel, Field, ConfigDict


class Instrument(BaseModel):
    name: str
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
