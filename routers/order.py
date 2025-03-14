from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Header

from database.repository.order_repository import OrderRepository
from models.order import (
    LimitOrder,
    CreateOrderResponse,
    LimitOrderBody,
    MarketOrderBody,
)
from models.ok import Ok

router_order = APIRouter()


@router_order.post("/api/v1/order/", summary="Create Order")
async def create_order_response(
    new_order: LimitOrderBody | MarketOrderBody,
    authorization: Annotated[str | None, Header()] = None,
) -> CreateOrderResponse:
    # здесь еще прикрутить авторизацию
    id = UUID("450934f2-c0ad-4fa8-aee4-6a5ce9da5ee6")
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
    return result


@router_order.delete("/api/v1/order/{order_id}", summary="Cancel Order")
def cancel_order_by_id(
    order_id: UUID, authorization: Annotated[str | None, Header()] = None
) -> Ok:
    # отменяем ордер
    return Ok()
