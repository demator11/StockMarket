from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from models.orm_models.order import LimitOrderBody, MarketOrderBody
from token_management import user_authorization
from database.repository.order_repository import OrderRepository
from database.repository.repositories import get_order_repository
from models.endpoints_models.order import (
    LimitOrderResponse,
    LimitOrderBodyRequest,
    MarketOrderBodyRequest,
    CreateOrderResponse,
    MarketOrderResponse,
    MarketOrderBodyResponse,
    LimitOrderBodyResponse,
)
from models.enum_models.order import OrderStatus
from models.endpoints_models.success_response import SuccessResponse

order_router = APIRouter()


@order_router.post("/api/v1/order/", summary="Create Order")
async def create_order_response(
    new_order: LimitOrderBodyRequest | MarketOrderBodyRequest,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
):
    if isinstance(new_order, LimitOrderBody):
        new_order = LimitOrderBody(
            direction=new_order.direction,
            ticker=new_order.ticker,
            qty=new_order.qty,
            price=new_order.price,
        )
        order = await order_repository.create_limit_order(
            new_order, authorization
        )
        return CreateOrderResponse(order_id=order.id)
    new_order = MarketOrderBody(
        direction=new_order.direction,
        ticker=new_order.ticker,
        qty=new_order.qty,
    )
    order = await order_repository.create_market_order(
        new_order, authorization
    )
    return CreateOrderResponse(order_id=order.id)


@order_router.get("/api/v1/order", summary="List Orders")
async def get_orders_list(
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> list[LimitOrderResponse | MarketOrderResponse]:
    result = await order_repository.get_all_order_list()
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


@order_router.get("/api/v1/order/{order_id}", summary="Get Order")
async def get_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> LimitOrderResponse | MarketOrderResponse:
    order = await order_repository.get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif order.price is None:
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


@order_router.delete("/api/v1/order/{order_id}", summary="Cancel Order")
async def cancel_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> SuccessResponse:
    result = await order_repository.update_order_status(
        order_id=order_id, status=OrderStatus.cancelled
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif result is False:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")
    return SuccessResponse()
