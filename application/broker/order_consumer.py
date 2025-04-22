from dataclasses import field

from aio_pika import IncomingMessage
from pydantic import BaseModel

from application.database.repository.app_config_repository import (
    AppConfigRepository,
)
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.database.repository.outbox_message_repository import (
    OutboxMessageRepository,
)
from application.models.database_models.balance import Balance
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
    deposit_balances: list[Balance] = field(default_factory=list)
    withdraw_balances: list[Balance] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    ticker_count: int = 0

    def add_order(self, order: UpdateOrder):
        self.changed_orders.append(order)

    def add_deposit_balance(self, balance: Balance):
        self.deposit_balances.append(balance)

    def add_withdraw_balance(self, balance: Balance):
        self.withdraw_balances.append(balance)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def clear_all(self):
        self.changed_orders.clear()
        self.deposit_balances.clear()
        self.withdraw_balances.clear()
        self.transactions.clear()


class OrderFillResult(BaseModel):
    order_update: UpdateOrder
    deposit_balance: Balance
    withdraw_balance: Balance
    transaction: Transaction
    deposit_ticker: str
    withdraw_ticker: str
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
    current_order: Order,
    matching_order: Order,
    filled_so_far: int,
    base_asset: str,
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

    assert matching_order.price is not None
    if current_order.direction == OrderDirection.sell:
        deposit_balance_update = Balance(
            user_id=matching_order.user_id,
            ticker=matching_order.ticker,
            qty=ticker_filled,
        )
        withdraw_balance_update = Balance(
            user_id=matching_order.user_id,
            ticker=base_asset,
            qty=ticker_filled * matching_order.price,
        )
        deposit_ticker = matching_order.ticker
        withdraw_ticker = base_asset
    else:
        deposit_balance_update = Balance(
            user_id=matching_order.user_id,
            ticker=base_asset,
            qty=ticker_filled * matching_order.price,
        )
        withdraw_balance_update = Balance(
            user_id=matching_order.user_id,
            ticker=matching_order.ticker,
            qty=ticker_filled,
        )
        deposit_ticker = base_asset
        withdraw_ticker = matching_order.ticker
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
        deposit_balance=deposit_balance_update,
        withdraw_balance=withdraw_balance_update,
        transaction=transaction,
        ticker_filled=ticker_filled,
        deposit_ticker=deposit_ticker,
        withdraw_ticker=withdraw_ticker,
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


async def add_current_balance(
    current_order: Order,
    deposit_ticker: str,
    withdraw_ticker: str,
    result: OrderProcessingResult,
) -> None:
    deposit_qty = 0
    withdraw_qty = 0
    for balance in result.withdraw_balances:
        deposit_qty += balance.qty
    for balance in result.deposit_balances:
        withdraw_qty += balance.qty
    result.add_deposit_balance(
        Balance(
            user_id=current_order.user_id,
            ticker=deposit_ticker,
            qty=deposit_qty,
        )
    )
    result.add_withdraw_balance(
        Balance(
            user_id=current_order.user_id,
            ticker=withdraw_ticker,
            qty=withdraw_qty,
        )
    )


async def processing_orders(
    current_order: Order, matching_orders: list[Order], base_asset: str
) -> OrderProcessingResult:
    result = OrderProcessingResult()
    fill_result = None
    for order in matching_orders:
        if result.ticker_count >= current_order.qty:
            break

        fill_result = await calculate_order_fill(
            current_order, order, result.ticker_count, base_asset
        )
        if fill_result:
            result.add_order(fill_result.order_update)
            result.add_deposit_balance(fill_result.deposit_balance)
            result.add_withdraw_balance(fill_result.withdraw_balance)
            result.add_transaction(fill_result.transaction)
            result.ticker_count += fill_result.ticker_filled
    if fill_result:
        await add_current_balance(
            current_order=current_order,
            deposit_ticker=fill_result.withdraw_ticker,
            withdraw_ticker=fill_result.deposit_ticker,
            result=result,
        )
    updated_current_order = await update_current_order_status(
        current_order, result.ticker_count
    )
    if current_order.status == OrderStatus.cancelled:
        result.clear_all()
        result.add_order(updated_current_order)
    elif current_order.filled > 0:
        result.add_order(updated_current_order)

    return result


async def update_orders(
    ticker: str, orders: list[UpdateOrder], order_repository: OrderRepository
) -> None:
    await order_repository.bulk_update(ticker, orders)


async def update_balances(
    current_order: Order,
    result: OrderProcessingResult,
    balance_repository: BalanceRepository,
) -> None:
    await balance_repository.bulk_adjust(
        ticker=current_order.ticker,
        deposit_balances=result.deposit_balances,
        withdraw_balances=result.withdraw_balances,
    )


async def create_transactions(
    transactions: list[Transaction],
    transaction_repository: TransactionRepository,
) -> None:
    await transaction_repository.bulk_create(transactions)


async def process_order_fill(
    current_order: Order,
    result: OrderProcessingResult,
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    balance_repository: BalanceRepository,
) -> None:
    if result.changed_orders:
        await update_orders(
            current_order.ticker, result.changed_orders, order_repository
        )

    if result.transactions:
        await create_transactions(result.transactions, transaction_repository)
        await update_balances(current_order, result, balance_repository)


async def process_order(
    message: IncomingMessage,
) -> None:
    async with async_session_factory.begin() as session:
        order_repository = OrderRepository(db_session=session)
        transaction_repository = TransactionRepository(db_session=session)
        balance_repository = BalanceRepository(db_session=session)
        outbox_message_repository = OutboxMessageRepository(db_session=session)
        app_config_repository = AppConfigRepository(db_session=session)

        current_order = Order.model_validate_json(message.body.decode())
        if not await order_repository.create(current_order):
            return
        try:
            lock_id = await order_repository.advisory_lock_by_ticker(
                current_order.ticker
            )

            matching_orders = await get_matching_orders(
                current_order, order_repository
            )
            print(matching_orders)
            base_asset = await app_config_repository.get("base_asset") or "RUB"

            processing_result = await processing_orders(
                current_order, matching_orders, base_asset
            )

            await process_order_fill(
                current_order=current_order,
                result=processing_result,
                order_repository=order_repository,
                transaction_repository=transaction_repository,
                balance_repository=balance_repository,
            )
            await outbox_message_repository.delete(current_order.id)
        finally:
            await order_repository.advisory_unlock(lock_id)
    await message.ack()
