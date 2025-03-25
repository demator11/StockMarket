from uuid import UUID

from sqlalchemy import select, insert, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.orm_models.balance import BalanceOrm
from application.models.database_models.balance import Balance


class BalanceRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def upsert(self, deposit: Balance) -> Balance:
        try:
            await self.db_session.execute(select(func.pg_advisory_lock(123)))
            check_ticker_exists = await self.db_session.scalars(
                select(BalanceOrm)
                .where(BalanceOrm.user_id == deposit.user_id)
                .where(BalanceOrm.ticker == deposit.ticker)
            )
            ticker = check_ticker_exists.one_or_none()
            if ticker is None:
                result = await self.db_session.scalars(
                    insert(BalanceOrm)
                    .values(
                        user_id=deposit.user_id,
                        ticker=deposit.ticker,
                        qty=deposit.qty,
                    )
                    .returning(BalanceOrm)
                )
                return Balance.model_validate(result.one())

            result = await self.db_session.scalars(
                update(BalanceOrm)
                .values(qty=ticker.qty + deposit.qty)
                .where(BalanceOrm.user_id == deposit.user_id)
                .where(BalanceOrm.ticker == deposit.ticker)
                .returning(BalanceOrm)
            )

            return Balance.model_validate(result.one())
        finally:
            await self.db_session.execute(select(func.pg_advisory_unlock(123)))

    async def get_user_by_id(self, user_id: UUID) -> list[Balance]:
        query = select(BalanceOrm).where(BalanceOrm.user_id == user_id)
        result = await self.db_session.scalars(query)
        if result is None:
            return []
        return [Balance.model_validate(row) for row in result.all()]
