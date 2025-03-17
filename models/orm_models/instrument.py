from pydantic import Field

from models.base import ModelBase


class Instrument(ModelBase):
    name: str
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
