from uuid import UUID

from sqlalchemy import select, insert

from database.engine import async_session_factory
from database.database_models.balance import BalanceOrm
from models.body_deposit import (
    Body_deposit_api_v1_balance_deposit_post,
    BodyDeposit,
)


class BalanceRepository:
    @staticmethod
    async def create_user_deposit(
        user_id: UUID, deposit: Body_deposit_api_v1_balance_deposit_post
    ):
        async with async_session_factory.begin() as session:
            await session.scalars(
                insert(BalanceOrm)
                .values(
                    user_id=user_id,
                    currency=deposit.ticker,
                    qty=deposit.amount,
                )
                .returning(BalanceOrm)
            )

    @staticmethod
    async def get_user_balance(user_id: UUID):
        async with async_session_factory.begin() as session:
            query = select(BalanceOrm).where(BalanceOrm.user_id == user_id)
            result = await session.execute(query)
            balance_dict = {}
            for x in result.scalars().all():
                deposit = BodyDeposit.from_orm(x)
                balance_dict[deposit.currency] = deposit.qty
            return balance_dict
