from dataclasses import field
from uuid import UUID

from aio_pika import IncomingMessage
from pydantic import BaseModel

from application.database.repository.outbox_message_repository import (
    OutboxMessageRepository,
)
from application.models.orm_models.user import UserOrm  # noqa
from application.database.engine import async_session_factory
from application.database.repository.order_repository import OrderRepository
from application.database.repository.transaction_repository import (
    TransactionRepository,
)
from application.models.database_models.order import (
    Order,
    OrderDirection,
    UpdateOrder,
    OrderStatus,
)
from application.models.database_models.transaction import Transaction


class OrderProcessingResult(BaseModel):
    changed_orders: list[UpdateOrder] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    ticker_count: int = 0

    def add_order(self, order: UpdateOrder):
        self.changed_orders.append(order)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def clear_all(self):
        self.changed_orders.clear()
        self.transactions.clear()


class OrderFillResult(BaseModel):
    order_update: UpdateOrder
    transaction: Transaction
    ticker_filled: int


async def get_matching_orders(
    current_order: Order, order_repository: OrderRepository
) -> list[Order]:
    if current_order.direction == OrderDirection.sell:
        return await order_repository.get_by_ticker(
            current_order.ticker,
            current_order.qty,
            OrderDirection.buy,
        )
    else:
        return await order_repository.get_by_ticker(
            current_order.ticker,
            current_order.qty,
            OrderDirection.sell,
        )


async def calculate_order_fill(
    current_order: Order, matching_order: Order, filled_so_far: int
) -> OrderFillResult | None:
    need = current_order.qty - filled_so_far
    available = matching_order.qty - matching_order.filled

    if current_order.price is None:
        if need >= available:
            ticker_filled = available
            matching_order.filled = matching_order.qty
            matching_order.status = OrderStatus.executed
        else:
            ticker_filled = need
            matching_order.filled += ticker_filled
            matching_order.status = OrderStatus.partially_executed
            current_order.status = OrderStatus.executed
    else:
        if matching_order.price != current_order.price:
            return None
        ticker_filled = min(need, available)
        matching_order.filled += ticker_filled
        if matching_order.filled < matching_order.qty:
            matching_order.status = OrderStatus.partially_executed
        else:
            matching_order.status = OrderStatus.executed

    order_update = UpdateOrder(
        id=matching_order.id,
        status=matching_order.status,
        filled=matching_order.filled,
    )
    transaction = Transaction(
        ticker=matching_order.ticker,
        qty=ticker_filled,
        price=matching_order.price,
    )

    return OrderFillResult(
        order_update=order_update,
        transaction=transaction,
        ticker_filled=ticker_filled,
    )


async def update_current_order_status(
    current_order: Order, ticker_count: int
) -> UpdateOrder:
    current_order.filled = ticker_count
    if (
        current_order.price is None
        and current_order.filled != current_order.qty
    ):
        current_order.status = OrderStatus.cancelled
    elif 0 < current_order.filled < current_order.qty:
        current_order.status = OrderStatus.partially_executed
    elif current_order.filled == current_order.qty:
        current_order.status = OrderStatus.executed

    return UpdateOrder(
        id=current_order.id,
        filled=current_order.filled,
        status=current_order.status,
        price=current_order.price,
    )


async def processing_orders(
    current_order: Order, matching_orders: list[Order]
) -> OrderProcessingResult:
    result = OrderProcessingResult()

    for order in matching_orders:
        if result.ticker_count >= current_order.qty:
            break

        fill_result = await calculate_order_fill(
            current_order, order, result.ticker_count
        )
        if fill_result:
            result.add_transaction(fill_result.transaction)
            result.add_order(fill_result.order_update)
            result.ticker_count += fill_result.ticker_filled

    updated_current_order = await update_current_order_status(
        current_order, result.ticker_count
    )
    if current_order.status == OrderStatus.cancelled:
        result.clear_all()
        result.add_order(updated_current_order)
    elif current_order.filled > 0:
        result.add_order(updated_current_order)

    return result


async def update_orders_and_create_transactions(
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    current_order: Order,
    result: OrderProcessingResult,
) -> None:
    if result.changed_orders:
        await order_repository.bulk_update(
            current_order.ticker, result.changed_orders
        )

    if result.transactions:
        await transaction_repository.bulk_create(result.transactions)


async def delete_outbox_message(
    message_id: UUID, outbox_message_repository: OutboxMessageRepository
) -> None:
    await outbox_message_repository.delete(message_id)


async def process_order(
    message: IncomingMessage,
) -> None:
    async with async_session_factory.begin() as session:
        order_repository = OrderRepository(db_session=session)
        transaction_repository = TransactionRepository(db_session=session)
        outbox_message_repository = OutboxMessageRepository(db_session=session)

        current_order = Order.model_validate_json(message.body.decode())
        try:
            lock_id = await order_repository.advisory_lock_by_ticker(
                current_order.ticker
            )

            if not await order_repository.create(current_order):
                return

            matching_orders = await get_matching_orders(
                current_order, order_repository
            )

            processing_result = await processing_orders(
                current_order, matching_orders
            )

            await update_orders_and_create_transactions(
                order_repository,
                transaction_repository,
                current_order,
                processing_result,
            )
            await delete_outbox_message(
                current_order.id, outbox_message_repository
            )
        finally:
            await order_repository.advisory_unlock(lock_id)
    await message.ack()
