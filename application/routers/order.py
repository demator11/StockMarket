from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from application.database.repository.outbox_message_repository import (
    OutboxMessageRepository,
)
from application.models.database_models.order import (
    UpdateOrder,
    OrderStatus,
    Order,
)
from application.models.database_models.outbox_message import OutboxMessage
from application.models.endpoint_models.order.get_order_list import (
    LimitOrderListResponse,
    LimitOrderBodyListResponse,
    MarketOrderListResponse,
    MarketOrderBodyListResponse,
)
from application.token_management import user_authorization
from application.database.repository.order_repository import OrderRepository
from application.di.repositories import (
    get_order_repository,
    get_outbox_message_repository,
)
from application.models.endpoint_models.order.get_order_by_id import (
    LimitOrderByIdResponse,
    MarketOrderByIdResponse,
    MarketOrderBodyByIdResponse,
    LimitOrderBodyByIdResponse,
)
from application.models.endpoint_models.order.create_order import (
    CreateOrderRequest,
    CreateOrderResponse,
)
from application.models.endpoint_models.success_response import (
    SuccessResponse,
)

order_router = APIRouter(prefix="/api/v1/order")


@order_router.post("/", summary="Create Order")
async def create_order(
    new_order: CreateOrderRequest,
    authorization: UUID = Depends(user_authorization),
    outbox_message_repository: OutboxMessageRepository = Depends(
        get_outbox_message_repository
    ),
) -> CreateOrderResponse:
    order_body = Order(
        status=OrderStatus.new,
        user_id=authorization,
        direction=new_order.direction,
        ticker=new_order.ticker,
        qty=new_order.qty,
        price=new_order.price,
    )
    await outbox_message_repository.create(
        OutboxMessage(
            id=order_body.id, payload=str(order_body.model_dump_json())
        )
    )
    return CreateOrderResponse(order_id=order_body.id)


@order_router.get("", summary="List Orders")
async def get_orders_list(
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> list[LimitOrderListResponse | MarketOrderListResponse]:
    result = await order_repository.get_all()
    order_list = []
    for order in result:
        if order.price is None:
            order_list.append(
                MarketOrderListResponse(
                    id=order.id,
                    status=order.status,
                    user_id=order.user_id,
                    body=MarketOrderBodyListResponse(
                        direction=order.direction,
                        ticker=order.ticker,
                        qty=order.qty,
                    ),
                )
            )
        else:
            order_list.append(
                LimitOrderListResponse(
                    id=order.id,
                    status=order.status,
                    user_id=order.user_id,
                    body=LimitOrderBodyListResponse(
                        direction=order.direction,
                        ticker=order.ticker,
                        qty=order.qty,
                        price=order.price,
                    ),
                    filled=order.filled,
                )
            )

    return order_list


@order_router.get("/{order_id}", summary="Get Order")
async def get_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> LimitOrderByIdResponse | MarketOrderByIdResponse:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    if order.price is None:
        return MarketOrderByIdResponse(
            id=order.id,
            status=order.status,
            user_id=order.user_id,
            body=MarketOrderBodyByIdResponse(
                direction=order.direction,
                ticker=order.ticker,
                qty=order.qty,
            ),
        )
    return LimitOrderByIdResponse(
        id=order.id,
        status=order.status,
        user_id=order.user_id,
        body=LimitOrderBodyByIdResponse(
            direction=order.direction,
            ticker=order.ticker,
            qty=order.qty,
            price=order.price,
        ),
        filled=order.filled,
    )


@order_router.delete("/{order_id}", summary="Cancel Order")
async def cancel_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> SuccessResponse:
    order_check = await order_repository.get_by_id(order_id)
    if order_check is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif order_check.status == OrderStatus.cancelled:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")

    await order_repository.update(
        UpdateOrder(id=order_id, status=OrderStatus.cancelled)
    )
    return SuccessResponse()
