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
from logger import setup_logging

logger = setup_logging(__name__)


class OrderProcessingResult(BaseModel):
    changed_orders: list[UpdateOrder] = field(default_factory=list)
    deposit_balances: list[Balance] = field(default_factory=list)
    withdraw_balances: list[Balance] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    ticker_count: int = 0
    final_cost: int = 0

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
            reserve=ticker_filled * matching_order.price,
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
            reserve=ticker_filled,
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
        status=current_order.status,
        user_id=current_order.user_id,
        direction=current_order.direction,
        ticker=current_order.ticker,
        qty=current_order.qty,
        price=current_order.price,
        filled=current_order.filled,
    )


async def add_current_balance(
    current_order: Order,
    deposit_ticker: str,
    withdraw_ticker: str,
    result: OrderProcessingResult,
) -> OrderProcessingResult:
    withdraw_qty = sum(balance.qty for balance in result.deposit_balances)
    deposit_qty = sum(balance.reserve for balance in result.withdraw_balances)

    result.add_deposit_balance(
        Balance(
            user_id=current_order.user_id,
            ticker=deposit_ticker,
            qty=deposit_qty,
        )
    )
    if current_order.price is None:
        if current_order.direction == OrderDirection.sell:
            result.add_withdraw_balance(
                Balance(
                    user_id=current_order.user_id,
                    ticker=withdraw_ticker,
                    reserve=withdraw_qty,
                )
            )
        else:
            result.add_withdraw_balance(
                Balance(
                    user_id=current_order.user_id,
                    ticker=withdraw_ticker,
                    qty=withdraw_qty,
                )
            )
    else:
        result.add_withdraw_balance(
            Balance(
                user_id=current_order.user_id,
                ticker=withdraw_ticker,
                reserve=withdraw_qty,
            )
        )
    return result


async def processing_cancelled_order(
    updated_current_order: UpdateOrder,
    result: OrderProcessingResult,
):
    result.clear_all()
    result.add_order(updated_current_order)
    if updated_current_order.direction == OrderDirection.sell:
        result.add_deposit_balance(
            Balance(
                user_id=updated_current_order.user_id,
                ticker=updated_current_order.ticker,
                qty=updated_current_order.qty,
            )
        )
        result.add_withdraw_balance(
            Balance(
                user_id=updated_current_order.user_id,
                ticker=updated_current_order.ticker,
                reserve=updated_current_order.qty,
            )
        )
    return result


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
            result.final_cost += (
                fill_result.transaction.price * fill_result.transaction.qty
            )

    updated_current_order = await update_current_order_status(
        current_order, result.ticker_count
    )
    if current_order.status == OrderStatus.cancelled:
        result = await processing_cancelled_order(
            updated_current_order=updated_current_order, result=result
        )
    elif current_order.filled > 0:
        assert fill_result is not None
        result.add_order(updated_current_order)
        result = await add_current_balance(
            current_order=current_order,
            deposit_ticker=fill_result.withdraw_ticker,
            withdraw_ticker=fill_result.deposit_ticker,
            result=result,
        )
    return result


async def update_orders(
    orders: list[UpdateOrder], order_repository: OrderRepository
) -> None:
    await order_repository.bulk_update(orders)


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
        await update_orders(result.changed_orders, order_repository)
        logger.info(f"Update orders: {result.changed_orders}")

    if result.transactions:
        await create_transactions(result.transactions, transaction_repository)
        logger.info(f"Create transactions: {result.transactions}")
    if result.deposit_balances:
        await update_balances(current_order, result, balance_repository)
        logger.info(f"Deposit balances: {result.deposit_balances}")
        logger.info(f"Withdraw balances: {result.withdraw_balances}")


async def accept_or_deny_operation(
    current_order: Order,
    base_asset: str,
    result: OrderProcessingResult,
    balance_repository: BalanceRepository,
) -> OrderProcessingResult:
    user_balance = await balance_repository.get_balance_by_user_id_and_ticker(
        current_order.user_id, base_asset
    )
    assert user_balance is not None
    if user_balance.qty < result.final_cost:
        result.clear_all()
        result.add_order(
            UpdateOrder(
                id=current_order.id,
                filled=current_order.filled,
                status=OrderStatus.cancelled,
                price=current_order.price,
            )
        )
        logger.info(f"Operation denied: {result}")
    return result


async def process_order(
    message: IncomingMessage,
) -> None:
    logger.info(f"New message received: {message}")
    async with async_session_factory.begin() as session:
        order_repository = OrderRepository(db_session=session)
        transaction_repository = TransactionRepository(db_session=session)
        balance_repository = BalanceRepository(db_session=session)
        outbox_message_repository = OutboxMessageRepository(db_session=session)
        app_config_repository = AppConfigRepository(db_session=session)

        current_order = Order.model_validate_json(message.body.decode())
        try:
            if not await order_repository.create(current_order):
                await outbox_message_repository.delete(current_order.id)
                logger.info(f"Outbox message deleted by id {current_order.id}")
                await message.ack()
                logger.info(f"Message {current_order} acked")
                return
            logger.info(f"Process order has started: {current_order}")
            lock_id = await order_repository.advisory_lock_by_ticker(
                current_order.ticker
            )
            logger.info(
                f"Obtained advisory lock {lock_id} by ticker {current_order.ticker}"  # noqa
            )

            matching_orders = await get_matching_orders(
                current_order, order_repository
            )
            base_asset = await app_config_repository.get("base_asset") or "RUB"

            processing_result = await processing_orders(
                current_order, matching_orders, base_asset
            )
            logger.info(f"Result of processing: {processing_result}")

            if (
                current_order.price is None
                and current_order.direction == OrderDirection.buy
            ):
                processing_result = await accept_or_deny_operation(
                    current_order=current_order,
                    base_asset=base_asset,
                    result=processing_result,
                    balance_repository=balance_repository,
                )

            await process_order_fill(
                current_order=current_order,
                result=processing_result,
                order_repository=order_repository,
                transaction_repository=transaction_repository,
                balance_repository=balance_repository,
            )
            await outbox_message_repository.delete(current_order.id)
            logger.info(f"Outbox message deleted by id {current_order.id}")
        except Exception as error:
            logger.error(
                f"Order failed: {current_order}, {error}", exc_info=True
            )
        finally:
            await order_repository.advisory_unlock(lock_id)
            logger.info(
                f"Removed advisory lock {lock_id} by ticker {current_order.ticker}"  # noqa
            )
    await message.ack()
    logger.info(f"Message {current_order} acked")
