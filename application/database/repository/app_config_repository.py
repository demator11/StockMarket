from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.database_models.app_config import AppConfig
from application.models.orm_models.app_config import AppConfigOrm


class AppConfigRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def upsert(self, config: AppConfig) -> None:
        config_exists = await self.db_session.scalars(
            select(AppConfigOrm).where(AppConfigOrm.key == config.key)
        )

        if config_exists.one_or_none() is None:
            await self.db_session.execute(
                insert(AppConfigOrm).values(
                    key=config.key,
                    value=config.value,
                )
            )
            return

        await self.db_session.execute(
            update(AppConfigOrm)
            .values(value=config.value)
            .where(AppConfigOrm.key == config.key)
        )

    async def get(self, key: str):
        result = await self.db_session.scalars(
            select(AppConfigOrm.value).where(AppConfigOrm.key == key)
        )
        return result.one_or_none()
