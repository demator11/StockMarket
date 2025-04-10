from uuid import UUID

from sqlalchemy import insert, select, update, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.orm_models.order import OrderOrm
from application.models.database_models.order import (
    Order,
    UpdateOrder,
    OrderDirection,
    OrderStatus,
)


class OrderRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, order: Order) -> Order | None:
        print(1)
        if not await self.db_session.scalars(
            select(OrderOrm).where(OrderOrm.id == order.id)
        ):
            return None
        print(2)
        result = await self.db_session.scalars(
            insert(OrderOrm)
            .values(
                id=order.id,
                status=OrderStatus(order.status),
                user_id=order.user_id,
                direction=OrderDirection(order.direction),
                ticker=order.ticker,
                qty=order.qty,
                price=order.price,
            )
            .returning(OrderOrm)
        )
        print(3)
        return Order.model_validate(result.one())

    async def get_all(self) -> list[Order]:
        result = await self.db_session.scalars(select(OrderOrm))
        order_list = [Order.model_validate(order) for order in result.all()]
        return order_list

    async def get_by_id(self, order_id: UUID) -> Order | None:
        result = await self.db_session.get(OrderOrm, order_id)
        if not result:
            return None
        return Order.model_validate(result)

    async def get_by_ticker(
        self, ticker: str, limit: int, direction: OrderDirection | None = None
    ) -> list[Order]:
        if direction is None:
            result = await self.db_session.scalars(
                select(OrderOrm).where(OrderOrm.ticker == ticker).limit(limit)
            )
        else:
            result = await self.db_session.scalars(
                select(OrderOrm)
                .where(OrderOrm.ticker == ticker)
                .where(OrderOrm.direction == direction)
                .where(
                    or_(
                        OrderOrm.status == OrderStatus.new,
                        OrderOrm.status == OrderStatus.partially_executed,
                    )
                )
                .order_by(OrderOrm.price)
            )
        order_list = [Order.model_validate(order) for order in result.all()]
        return order_list

    async def update(self, params: UpdateOrder) -> None:
        update_values = params.dict(exclude_unset=True, exclude={"id"})
        await self.db_session.execute(
            update(OrderOrm)
            .where(OrderOrm.id == params.id)
            .values(**update_values)
        )

    async def bulk_update(
        self, ticker: str, orders: list[UpdateOrder]
    ) -> None:
        await self.db_session.execute(
            update(OrderOrm),
            [order.dict(exclude_none=True) for order in orders],
        )

    async def advisory_lock_by_ticker(self, ticker) -> int:
        lock_id = hash(ticker)
        await self.db_session.execute(
            select(func.pg_advisory_lock(lock_id)).where(
                OrderOrm.ticker == ticker
            )
        )
        return lock_id

    async def advisory_unlock(self, lock_id: int) -> None:
        await self.db_session.execute(select(func.pg_advisory_unlock(lock_id)))
