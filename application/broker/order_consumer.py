from aio_pika import IncomingMessage

from application.database.repository.order_repository import OrderRepository
from application.models.database_models.order import (
    Order,
    OrderDirection,
    Ticker,
)
from application.models.database_models.transaction import Transaction


async def process_order(
    message: IncomingMessage, order_repository: OrderRepository
) -> None:
    current_order = Order.model_validate_json(message.body.decode())
    if current_order.direction == OrderDirection.sell:
        orders = await order_repository.get_by_ticker(
            Ticker(ticker=current_order.ticker, limit=current_order.qty),
            OrderDirection.buy,
        )
    else:
        orders = await order_repository.get_by_ticker(
            Ticker(ticker=current_order.ticker, limit=current_order.qty),
            OrderDirection.sell,
        )
    changed_orders_list = []
    transactions_list = []
    ticker_count = 0
    for order in orders:
        if ticker_count == current_order.qty:
            break
        amount_need_ticker = current_order.qty - ticker_count
        amount_available_ticker = order.qty - order.filled
        if current_order.price is None:
            if amount_need_ticker >= amount_available_ticker:
                ticker_filled = amount_available_ticker
                order.filled = order.qty
                ticker_count += ticker_filled
                changed_orders_list.append(order)
            else:
                ticker_filled = amount_need_ticker
                order.filled += ticker_filled
                ticker_count += ticker_filled
                changed_orders_list.append(order)

        else:
            if order.price != current_order.price:
                break
            ticker_filled = min(amount_need_ticker, amount_available_ticker)
            order.filled += ticker_filled
            current_order.filled += ticker_filled
            ticker_count += ticker_filled
            changed_orders_list.append(order)

        transactions_list.append(
            Transaction(
                ticker=current_order.ticker,
                qty=ticker_filled,
                price=order.price,
            )
        )
    current_order.filled = ticker_count
    if (
        current_order.price is None
        and current_order.filled != current_order.qty
    ):
        changed_orders_list = []
    changed_orders_list.append(current_order)
    await message.ack()
