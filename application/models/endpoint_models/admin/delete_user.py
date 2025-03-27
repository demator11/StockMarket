from uuid import UUID

from pydantic import BaseModel

from application.models.database_models.user import UserRole


class DeleteUserResponse(BaseModel):
    id: UUID
    name: str
    role: UserRole
    api_key: str
