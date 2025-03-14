from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Header

from database.repository.order_repository import OrderRepository
from models.order import LimitOrderBody, LimitOrder, CreateOrderResponse
from models.ok import Ok

router_order = APIRouter()


@router_order.post("/api/v1/order/", summary="Create Order")
async def create_order_response(
    new_order: LimitOrderBody,
    authorization: Annotated[str | None, Header()] = None,
) -> CreateOrderResponse:
    # здесь еще прикрутить авторизацию

    order_type = "limit"
    try:
        new_order.price
    except KeyError:
        order_type = "market"
    result = await OrderRepository.create_order(
        new_order, UUID("ea32f146-7dad-4ac8-9393-d18b5d41f10e"), order_type
    )

    return result


@router_order.get("/api/v1/order", summary="List Orders")
async def get_orders_list(
    authorization: Annotated[str | None, Header()] = None,
) -> list[LimitOrder]:
    result = await OrderRepository.get_order_list()
    return result


@router_order.get("/api/v1/order/{order_id}", summary="Get Order")
def get_order_by_id(
    order_id: UUID, authorization: Annotated[str | None, Header()] = None
) -> LimitOrder:
    # получаем нужный order
    return LimitOrder()


@router_order.delete("/api/v1/order/{order_id}", summary="Cancel Order")
def cancel_order_by_id(
    order_id: UUID, authorization: Annotated[str | None, Header()] = None
) -> Ok:
    # отменяем ордер
    return Ok()
