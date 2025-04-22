from datetime import datetime

from pydantic import Field

from application.models.base import ModelBase


class AppConfig(ModelBase):
    key: str
    value: str
    timestamp: datetime = Field(default_factory=datetime.now)
