from uuid import UUID

from sqlalchemy import insert, select, update

from models.order import (
    MarketOrderBody,
    LimitOrderBody,
    CreateOrderResponse,
    RawOrder,
    MarketOrder,
    LimitOrder,
    Direction,
    OrderStatus,
)
from database.database_models.order import OrderOrm
from database.engine import async_session_factory


class OrderRepository:
    @staticmethod
    async def create_limit_order(
        new_order: LimitOrderBody,
        user_id: UUID,
    ):
        async with async_session_factory.begin() as session:
            result = await session.scalars(
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
                .returning(OrderOrm.id)
            )
            return CreateOrderResponse(order_id=result.one())

    @staticmethod
    async def create_market_order(
        new_order: MarketOrderBody,
        user_id: UUID,
    ):
        async with async_session_factory.begin() as session:
            result = await session.scalars(
                insert(OrderOrm)
                .values(
                    order_type="market",
                    status="NEW",
                    user_id=user_id,
                    direction=Direction(new_order.direction),
                    ticker=new_order.ticker,
                    qty=new_order.qty,
                )
                .returning(OrderOrm.id)
            )
            return CreateOrderResponse(order_id=result.one())

    @staticmethod
    async def get_order_list():
        async with async_session_factory.begin() as session:
            query = select(OrderOrm)
            result = await session.execute(query)
            order_list = []
            for order in result.scalars().all():
                order_model = RawOrder.from_orm(order)
                if order_model.order_type == "market":
                    order_list.append(
                        MarketOrder(
                            id=order_model.id,
                            status=order_model.status,
                            user_id=order_model.user_id,
                            body=MarketOrderBody(
                                direction=order_model.direction,
                                ticker=order_model.ticker,
                                qty=order_model.qty,
                            ),
                        )
                    )
                else:
                    order_list.append(
                        LimitOrder(
                            id=order_model.id,
                            status=order_model.status,
                            user_id=order_model.user_id,
                            body=LimitOrderBody(
                                direction=order_model.direction,
                                ticker=order_model.ticker,
                                qty=order_model.qty,
                                price=order_model.price,
                            ),
                            filled=order_model.filled,
                        )
                    )
            return order_list

    @staticmethod
    async def get_order_by_id(order_id: UUID):
        async with async_session_factory.begin() as session:
            order = await session.get(OrderOrm, order_id)
            if not order:
                return None
            order_model = RawOrder.from_orm(order)
            if order_model.order_type == "market":
                return MarketOrder(
                    id=order_model.id,
                    status=order_model.status,
                    user_id=order_model.user_id,
                    body=MarketOrderBody(
                        direction=order_model.direction,
                        ticker=order_model.ticker,
                        qty=order_model.qty,
                    ),
                )
            return LimitOrder(
                id=order_model.id,
                status=order_model.status,
                user_id=order_model.user_id,
                body=LimitOrderBody(
                    direction=order_model.direction,
                    ticker=order_model.ticker,
                    qty=order_model.qty,
                    price=order_model.price,
                ),
                filled=order_model.filled,
            )

    @staticmethod
    async def update_order_status(order_id: UUID, status: OrderStatus):
        async with async_session_factory.begin() as session:
            order = await session.get(OrderOrm, order_id)
            if not order:
                return None
            if order.status == OrderStatus.cancelled:
                return False
            return await session.execute(
                update(OrderOrm)
                .where(OrderOrm.id == order_id)
                .values(status=status)
            )
