from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.database_models.transaction import Transaction
from application.models.orm_models.transaction import TransactionOrm


class TransactionRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, transaction: Transaction) -> None:
        await self.db_session.execute(
            insert(TransactionOrm).values(
                ticker=transaction.ticker,
                qty=transaction.qty,
                price=transaction.price,
            )
        )

    async def bulk_create(self, transactions: list[Transaction]):
        await self.db_session.execute(
            insert(TransactionOrm),
            [
                transaction.dict(exclude_unset=True)
                for transaction in transactions
            ],
        )

    async def get(self, ticker: str, limit: int) -> list[Transaction]:
        result = await self.db_session.scalars(
            select(TransactionOrm)
            .where(TransactionOrm.ticker == ticker)
            .limit(limit)
        )
        transaction_list = [
            Transaction.model_validate(row) for row in result.all()
        ]
        return transaction_list
