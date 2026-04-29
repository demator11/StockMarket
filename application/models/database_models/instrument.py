from application.models.base import ModelBase


class Instrument(ModelBase):
    name: str
    ticker: str
