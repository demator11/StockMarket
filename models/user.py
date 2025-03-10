from pydantic import BaseModel, Field
from enum import Enum


class UserRole(Enum):
    user = "USER"
    admin = "ADMIN"


class NewUser(BaseModel):
    name: str = Field(min_length=3)


class User(BaseModel):
    id: str
    name: str
    role: UserRole = UserRole.user
    api_key: str
