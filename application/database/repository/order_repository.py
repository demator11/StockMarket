from uuid import UUID

from sqlalchemy import insert, select, update
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

    async def create(self, order: Order) -> Order:
        result = await self.db_session.scalars(
            insert(OrderOrm)
            .values(
                status=OrderStatus(order.status),
                user_id=order.user_id,
                direction=OrderDirection(order.direction),
                ticker=order.ticker,
                qty=order.qty,
                price=order.price,
            )
            .returning(OrderOrm)
        )
        return Order.model_validate(result.one())

    async def get_all(self) -> list[Order]:
        query = select(OrderOrm)
        result = await self.db_session.scalars(query)
        order_list = [Order.from_orm(order) for order in result.all()]
        return order_list

    async def get_by_id(self, order_id: UUID) -> Order | None:
        result = await self.db_session.get(OrderOrm, order_id)
        if not result:
            return None
        return Order.model_validate(result)

    async def update(self, params: UpdateOrder) -> None:
        update_values = params.dict(exclude_unset=True, exclude={"id"})
        await self.db_session.scalars(
            update(OrderOrm)
            .where(OrderOrm.id == params.id)
            .values(**update_values)
            .returning(OrderOrm)
        )
