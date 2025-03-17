from uuid import UUID

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.database_models.user import UserOrm
from models.endpoints_models.user import User, NewUser
from models.enum_models.user import UserRole


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, new_user: NewUser, api_key: str) -> User:
        result = await self.db_session.scalars(
            insert(UserOrm)
            .values(name=new_user.name, role=UserRole.user, api_key=api_key)
            .returning(UserOrm)
        )
        return User.from_orm(result.one())

    async def check_user_in_database(self, user_name: str) -> bool:
        query = select(UserOrm.name).where(UserOrm.name == user_name)
        result = await self.db_session.scalars(query)
        if result.first() is None:
            return False
        return True

    async def check_user_authorization(self, api_key: str):
        query = select(UserOrm.id).where(UserOrm.api_key == api_key)
        result = await self.db_session.scalars(query)
        result = result.first()
        if result is None:
            return None
        return result

    async def check_admin_authorization(self, api_key: str):
        query = select(UserOrm.role).filter(UserOrm.api_key == api_key)
        result = await self.db_session.scalars(query)
        result = result.first()
        if result is None:
            return None
        elif result == "ADMIN":
            return True
        return False

    async def change_user_role(self, user_id: UUID, role: UserRole):
        await self.db_session.execute(
            update(UserOrm).where(UserOrm.id == user_id).values(role=role)
        )
