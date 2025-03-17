from uuid import UUID

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.database_models.user import UserOrm
from models.orm_models.user import User, NewUser
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

    async def exists_in_database(self, user_name: str) -> bool:
        query = select(UserOrm.name).where(UserOrm.name == user_name)
        result = await self.db_session.scalars(query)
        if result.first() is None:
            return False
        return True

    async def get_user_by_api_key(self, api_key: str) -> User | None:
        query = select(UserOrm).where(UserOrm.api_key == api_key)
        result = await self.db_session.scalars(query)
        user = User.from_orm(result.first())
        if user is None:
            return None
        return user

    async def check_admin_authorization(self, api_key: str) -> bool | None:
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
