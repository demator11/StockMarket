from uuid import UUID

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.database_models.balance import BalanceOrm
from application.models.orm_models.balance import Balance
from application.models.orm_models.deposit import NewDeposit


class BalanceRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user_deposit(self, deposit: NewDeposit) -> None:
        await self.db_session.scalars(
            insert(BalanceOrm)
            .values(
                user_id=deposit.user_id,
                ticker=deposit.ticker,
                qty=deposit.qty,
            )
            .returning(BalanceOrm)
        )

    async def get_user_by_id(self, user_id: UUID) -> list[Balance] | None:
        query = select(BalanceOrm).where(BalanceOrm.user_id == user_id)
        result = await self.db_session.execute(query)
        if result is None:
            return None
        return [Balance.model_validate(row) for row in result.scalars().all()]
