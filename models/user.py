from uuid import UUID
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict


class UserRole(StrEnum):
    user = "USER"
    admin = "ADMIN"


class NewUser(BaseModel):
    name: str = Field(min_length=3)


class User(BaseModel):
    id: UUID
    name: str
    role: UserRole = UserRole.user
    api_key: str

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
