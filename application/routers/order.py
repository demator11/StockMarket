from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from application.models.database_models.order import (
    OrderBody,
    UpdateOrder,
)
from application.token_management import user_authorization
from application.database.repository.order_repository import OrderRepository
from application.di.repositories import get_order_repository
from application.models.endpoint_models.order import (
    LimitOrderResponse,
    CreateOrderResponse,
    MarketOrderResponse,
    MarketOrderBodyResponse,
    LimitOrderBodyResponse,
    CreateOrderBodyRequest,
)
from application.models.enum_models.order import OrderStatus
from application.models.endpoint_models.success_response import (
    SuccessResponse,
)

order_router = APIRouter(prefix="/api/v1/order")


@order_router.post("/", summary="Create Order")
async def create_order_response(
    new_order: CreateOrderBodyRequest,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> CreateOrderResponse:
    order_body = OrderBody(
        direction=new_order.direction,
        ticker=new_order.ticker,
        qty=new_order.qty,
        price=new_order.price,
    )
    order = await order_repository.create(authorization, order_body)
    return CreateOrderResponse(order_id=order.id)


@order_router.get("", summary="List Orders")
async def get_orders_list(
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> list[LimitOrderResponse | MarketOrderResponse]:
    result = await order_repository.get_all()
    order_list = []
    for order in result:
        if order.price is None:
            order_list.append(
                MarketOrderResponse(
                    id=order.id,
                    status=order.status,
                    user_id=order.user_id,
                    body=MarketOrderBodyResponse(
                        direction=order.direction,
                        ticker=order.ticker,
                        qty=order.qty,
                    ),
                )
            )
        else:
            order_list.append(
                LimitOrderResponse(
                    id=order.id,
                    status=order.status,
                    user_id=order.user_id,
                    body=LimitOrderBodyResponse(
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
) -> LimitOrderResponse | MarketOrderResponse:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    if order.price is None:
        return MarketOrderResponse(
            id=order.id,
            status=order.status,
            user_id=order.user_id,
            body=MarketOrderBodyResponse(
                direction=order.direction,
                ticker=order.ticker,
                qty=order.qty,
            ),
        )
    return LimitOrderResponse(
        id=order.id,
        status=order.status,
        user_id=order.user_id,
        body=LimitOrderBodyResponse(
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
