from uuid import UUID

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.orm_models.balance import BalanceOrm
from application.models.database_models.balance import Balance
from application.models.database_models.deposit import Deposit


class BalanceRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def upsert_user_deposit(self, deposit: Deposit) -> Balance:
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

    async def get_user_by_id(self, user_id: UUID) -> list[Balance]:
        query = select(BalanceOrm).where(BalanceOrm.user_id == user_id)
        result = await self.db_session.scalars(query)
        if result is None:
            return []
        return [Balance.model_validate(row) for row in result.all()]
