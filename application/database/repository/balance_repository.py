from uuid import UUID

from sqlalchemy import select, insert, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.orm_models.balance import BalanceOrm
from application.models.database_models.balance import Balance


class BalanceRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def upsert(self, deposit: Balance) -> Balance:
        lock_id = hash(deposit.ticker)
        try:
            await self.db_session.execute(
                select(func.pg_advisory_lock(lock_id)).where(
                    BalanceOrm.ticker == deposit.ticker
                )
            )

            ticker_exists = await self.db_session.scalars(
                select(BalanceOrm)
                .where(BalanceOrm.user_id == deposit.user_id)
                .where(BalanceOrm.ticker == deposit.ticker)
            )
            ticker = ticker_exists.one_or_none()

            if ticker is None:
                result = await self.db_session.scalars(
                    insert(BalanceOrm)
                    .values(
                        user_id=deposit.user_id,
                        ticker=deposit.ticker,
                        qty=deposit.qty,
                        reserve=deposit.reserve,
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
            await self.db_session.execute(
                select(func.pg_advisory_unlock(lock_id))
            )

    async def get_balances_by_user_id(self, user_id: UUID) -> list[Balance]:
        result = await self.db_session.scalars(
            select(BalanceOrm).where(BalanceOrm.user_id == user_id)
        )
        if result is None:
            return []
        return [Balance.model_validate(row) for row in result.all()]

    async def get_balance_by_user_id_and_ticker(
        self, user_id: UUID, ticker: str
    ) -> Balance | None:
        result = await self.db_session.scalars(
            select(BalanceOrm)
            .where(BalanceOrm.user_id == user_id)
            .where(BalanceOrm.ticker == ticker)
        )
        result = result.one_or_none()
        if result is None:
            return None
        return Balance.model_validate(result)

    async def withdraw(self, withdraw: Balance) -> Balance | None:
        ticker_exists = await self.db_session.scalars(
            select(BalanceOrm)
            .where(BalanceOrm.user_id == withdraw.user_id)
            .where(BalanceOrm.ticker == withdraw.ticker)
        )
        ticker = ticker_exists.one_or_none()
        if ticker is None:
            return None
        elif ticker.qty < withdraw.qty:
            result = await self.db_session.scalars(
                update(BalanceOrm)
                .values(qty=0)
                .where(BalanceOrm.user_id == withdraw.user_id)
                .where(BalanceOrm.ticker == withdraw.ticker)
                .returning(BalanceOrm)
            )
            return Balance.model_validate(result.one())
        result = await self.db_session.scalars(
            update(BalanceOrm)
            .values(qty=BalanceOrm.qty - withdraw.qty)
            .where(BalanceOrm.user_id == withdraw.user_id)
            .where(BalanceOrm.ticker == withdraw.ticker)
            .returning(BalanceOrm)
        )
        return Balance.model_validate(result.one())

    async def reserve(self, balance: Balance) -> None:
        await self.db_session.execute(
            update(BalanceOrm)
            .values(
                qty=BalanceOrm.qty - balance.reserve,
                reserve=BalanceOrm.reserve + balance.reserve,
            )
            .where(BalanceOrm.user_id == balance.user_id)
            .where(BalanceOrm.ticker == balance.ticker)
        )

    async def release(self, balance: Balance) -> None:
        await self.db_session.execute(
            update(BalanceOrm)
            .values(
                qty=BalanceOrm.qty + balance.reserve,
                reserve=BalanceOrm.reserve - balance.reserve,
            )
            .where(BalanceOrm.user_id == balance.user_id)
            .where(BalanceOrm.ticker == balance.ticker)
        )

    async def bulk_adjust(
        self,
        ticker: str,
        deposit_balances: list[Balance],
        withdraw_balances: list[Balance],
    ) -> None:
        lock_id = hash(ticker)
        try:
            await self.db_session.execute(
                select(func.pg_advisory_lock(lock_id)).where(
                    BalanceOrm.ticker == ticker
                )
            )
            print(deposit_balances)
            for deposit in deposit_balances:
                ticker_exists = await self.db_session.scalars(
                    select(BalanceOrm)
                    .where(BalanceOrm.user_id == deposit.user_id)
                    .where(BalanceOrm.ticker == deposit.ticker)
                )
                ticker_body = ticker_exists.one_or_none()

                if ticker_body is None:
                    await self.db_session.execute(
                        insert(BalanceOrm).values(
                            user_id=deposit.user_id,
                            ticker=deposit.ticker,
                            qty=deposit.qty,
                            reserve=deposit.reserve,
                        )
                    )
                else:
                    await self.db_session.execute(
                        update(BalanceOrm)
                        .values(qty=ticker_body.qty + deposit.qty)
                        .where(BalanceOrm.user_id == deposit.user_id)
                        .where(BalanceOrm.ticker == deposit.ticker)
                    )

            for withdraw in withdraw_balances:
                ticker_exists = await self.db_session.scalars(
                    select(BalanceOrm)
                    .where(BalanceOrm.user_id == withdraw.user_id)
                    .where(BalanceOrm.ticker == withdraw.ticker)
                )
                ticker_body = ticker_exists.one_or_none()
                if ticker_body is None:
                    return None
                else:
                    await self.db_session.execute(
                        update(BalanceOrm)
                        .values(
                            qty=BalanceOrm.qty - withdraw.qty,
                            reserve=BalanceOrm.reserve - withdraw.reserve,
                        )
                        .where(BalanceOrm.user_id == withdraw.user_id)
                        .where(BalanceOrm.ticker == withdraw.ticker)
                    )

        finally:
            await self.db_session.execute(
                select(func.pg_advisory_unlock(lock_id))
            )
