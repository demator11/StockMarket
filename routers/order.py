from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException

from database.repository.order_repository import OrderRepository
from models.order import (
    LimitOrder,
    CreateOrderResponse,
    LimitOrderBody,
    MarketOrderBody,
    OrderStatus,
)
from models.ok import Ok

router_order = APIRouter()


@router_order.post("/api/v1/order/", summary="Create Order")
async def create_order_response(
    new_order: LimitOrderBody | MarketOrderBody,
    authorization: Annotated[str | None, Header()] = None,
) -> CreateOrderResponse:
    # здесь еще прикрутить авторизацию
    id = UUID("e9885be4-aecb-4fe9-a4d3-5dd40dee9ec9")
    # а сюда еще проверку сущетсвует ли такой тикер
    try:
        new_order.price
    except AttributeError:
        return await OrderRepository.create_market_order(new_order, id)
    return await OrderRepository.create_limit_order(new_order, id)


@router_order.get("/api/v1/order", summary="List Orders")
async def get_orders_list(
    authorization: Annotated[str | None, Header()] = None,
):
    result = await OrderRepository.get_order_list()
    return result


@router_order.get("/api/v1/order/{order_id}", summary="Get Order")
async def get_order_by_id(
    order_id: UUID, authorization: Annotated[str | None, Header()] = None
) -> LimitOrder:
    result = await OrderRepository.get_order_by_id(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    return result


@router_order.delete("/api/v1/order/{order_id}", summary="Cancel Order")
async def cancel_order_by_id(
    order_id: UUID, authorization: Annotated[str | None, Header()] = None
) -> Ok:

    result = await OrderRepository.update_order_status(
        order_id=order_id, status=OrderStatus.cancelled
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif not result:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")
    return Ok()
