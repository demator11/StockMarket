from uuid import UUID

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.database_models.balance import BalanceOrm
from models.endpoints_models.body_deposit import (
    Body_deposit_api_v1_balance_deposit_post,
)
from models.orm_models.deposit import Deposit


class BalanceRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user_deposit(self, user_id: UUID, deposit: Deposit):
        await self.db_session.scalars(
            insert(BalanceOrm)
            .values(
                user_id=user_id,
                currency=deposit.ticker,
                qty=deposit.amount,
            )
            .returning(BalanceOrm)
        )

    async def get_user_balance(self, user_id: UUID):
        query = select(BalanceOrm).where(BalanceOrm.user_id == user_id)
        result = await self.db_session.execute(query)
        balance_dict = {}
        for x in result.scalars().all():
            deposit = Deposit.from_orm(x)
            balance_dict[deposit.currency] = deposit.qty
        return balance_dict
