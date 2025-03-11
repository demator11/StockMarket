from typing import Annotated
from fastapi import APIRouter, Header

from models.order import LimitOrderBody, CreateOrderResponse

router_order = APIRouter()


@router_order.get("/api/v1/order/")
def create_order_response(
    new_order: LimitOrderBody, api_key: Annotated[str | None, Header()] = None
) -> CreateOrderResponse:
    # создаем order и присваиваем id
    order_id = 123
    return CreateOrderResponse(order_id=order_id)
