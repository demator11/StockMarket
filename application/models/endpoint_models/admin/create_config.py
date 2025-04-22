from pydantic import BaseModel


class CreateConfigRequest(BaseModel):
    key: str
    value: str
