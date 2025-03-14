from uuid import UUID

from sqlalchemy import insert

from models.order import MarketOrderBody, LimitOrderBody, CreateOrderResponse
from database.database_models.order import OrderOrm
from database.engine import async_session_factory


class OrderRepository:
    @staticmethod
    async def create_order(
        new_order: MarketOrderBody | LimitOrderBody,
        user_id: UUID,
        order_type: str,
    ):
        async with async_session_factory.begin() as session:
            result = await session.scalars(
                insert(OrderOrm)
                .values(
                    order_type=order_type,
                    status="NEW",
                    user_id=user_id,
                    direction=new_order.direction,
                    ticker=new_order.ticker,
                    qty=new_order.qty,
                    price=new_order.price,
                )
                .returning(OrderOrm.id)
            )
            return CreateOrderResponse(order_id=result.one())
