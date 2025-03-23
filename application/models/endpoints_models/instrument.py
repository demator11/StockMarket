from pydantic import Field

from application.models.base import ModelBase


class InstrumentRequest(ModelBase):
    name: str
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
