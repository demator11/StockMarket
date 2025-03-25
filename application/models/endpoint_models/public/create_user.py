from uuid import UUID

from pydantic import Field, BaseModel

from application.models.database_models.user import UserRole


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=3)


class CreateUserResponse(BaseModel):
    id: UUID
    name: str
    role: UserRole = UserRole.user
    api_key: str
