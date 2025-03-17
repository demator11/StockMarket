from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.enum_models.order import Direction, OrderStatus
from models.database_models.order import OrderOrm
from models.orm_models.order import (
    LimitOrderBody,
    Order,
    MarketOrderBody,
    LimitOrder,
    MarketOrder,
)


class OrderRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_limit_order(
        self,
        new_order: LimitOrderBody,
        user_id: UUID,
    ) -> Order:
        result = await self.db_session.scalars(
            insert(OrderOrm)
            .values(
                order_type="limit",
                status=OrderStatus.new,
                user_id=user_id,
                direction=Direction(new_order.direction),
                ticker=new_order.ticker,
                qty=new_order.qty,
                price=new_order.price,
            )
            .returning(OrderOrm)
        )
        return Order.from_orm(result.one())

    async def create_market_order(
        self,
        new_order: MarketOrderBody,
        user_id: UUID,
    ) -> Order:
        result = await self.db_session.scalars(
            insert(OrderOrm)
            .values(
                order_type="market",
                status="NEW",
                user_id=user_id,
                direction=Direction(new_order.direction),
                ticker=new_order.ticker,
                qty=new_order.qty,
            )
            .returning(OrderOrm)
        )
        return Order.from_orm(result.one())

    async def get_all_order_list(self) -> list[Order]:
        query = select(OrderOrm)
        result = await self.db_session.execute(query)
        order_list = [
            Order.from_orm(order) for order in result.scalars().all()
        ]
        return order_list

    async def get_order_by_id(self, order_id: UUID) -> Order | None:
        result = await self.db_session.get(OrderOrm, order_id)
        if not result:
            return None
        return Order.from_orm(result)

    async def update_order_status(
        self, order_id: UUID, status: OrderStatus
    ) -> bool | None:
        order = await self.db_session.get(OrderOrm, order_id)
        print(order)
        if order is None:
            return None
        elif order.status == OrderStatus.cancelled:
            return False
        await self.db_session.execute(
            update(OrderOrm)
            .where(OrderOrm.id == order_id)
            .values(status=status)
        )
        return True
