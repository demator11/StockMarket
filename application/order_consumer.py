from dataclasses import field
from uuid import UUID

from pydantic import BaseModel

from application.database.repository.app_config_repository import (
    AppConfigRepository,
)
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.models.database_models.balance import Balance
from application.models.orm_models.user import UserOrm  # noqa
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
    status_code: int = 200
    detail: str | None = None

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


class OrderFinalResult(BaseModel):
    status_code: int = 200
    order_id: UUID
    detail: str | None = None


async def get_matching_orders(
    current_order: Order, order_repository: OrderRepository
) -> list[Order]:
    """
    Возвращает список ордеров, которые соответствуют текущему
    ордеру по тикеру и количеству.
    """
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


async def update_result(
    current_order: Order,
    matching_order: Order,
    ticker_filled: int,
    ticker_price: int,
    base_asset: str,
    result: OrderProcessingResult,
) -> OrderProcessingResult:
    """
    Обновляет результат обработки ордера, добавляя информацию о сделке,
    измененных балансах и транзакциях.
    """
    assert matching_order.price is not None
    if current_order.price is not None:
        difference = abs(current_order.price - matching_order.price)
        if matching_order.price < current_order.price:
            result.add_deposit_balance(
                Balance(
                    user_id=current_order.user_id,
                    ticker=base_asset,
                    qty=difference * ticker_filled,
                )
            )
            result.add_withdraw_balance(
                Balance(
                    user_id=current_order.user_id,
                    ticker=base_asset,
                    reserve=difference * ticker_filled,
                )
            )

    if current_order.direction == OrderDirection.sell:
        deposit_qty = ticker_filled
        withdraw_qty = ticker_filled * ticker_price
        deposit_ticker = matching_order.ticker
        withdraw_ticker = base_asset
        result.add_deposit_balance(
            Balance(
                user_id=matching_order.user_id,
                ticker=deposit_ticker,
                qty=deposit_qty,
            )
        )
        result.add_withdraw_balance(
            Balance(
                user_id=matching_order.user_id,
                ticker=withdraw_ticker,
                reserve=withdraw_qty,
            )
        )

    else:
        deposit_qty = ticker_filled * ticker_price
        withdraw_qty = ticker_filled
        deposit_ticker = base_asset
        withdraw_ticker = matching_order.ticker
        result.add_deposit_balance(
            Balance(
                user_id=matching_order.user_id,
                ticker=deposit_ticker,
                qty=deposit_qty,
            )
        )
        result.add_withdraw_balance(
            Balance(
                user_id=matching_order.user_id,
                ticker=withdraw_ticker,
                reserve=withdraw_qty,
            )
        )
    result.add_deposit_balance(
        Balance(
            user_id=current_order.user_id,
            ticker=withdraw_ticker,
            qty=withdraw_qty,
        )
    )
    if (
        current_order.price is None
        and current_order.direction != OrderDirection.sell
    ):
        result.add_withdraw_balance(
            Balance(
                user_id=current_order.user_id,
                ticker=deposit_ticker,
                qty=deposit_qty,
            )
        )
    else:
        result.add_withdraw_balance(
            Balance(
                user_id=current_order.user_id,
                ticker=deposit_ticker,
                reserve=deposit_qty,
            )
        )

    result.add_order(
        UpdateOrder(
            id=matching_order.id,
            status=matching_order.status,
            filled=matching_order.filled,
        )
    )
    result.add_transaction(
        Transaction(
            ticker=matching_order.ticker,
            qty=ticker_filled,
            price=ticker_price,
            timestamp=current_order.timestamp,
        )
    )
    result.ticker_count += ticker_filled
    result.final_cost += ticker_price * ticker_filled

    return result


async def calculate_order_fill(
    current_order: Order,
    matching_order: Order,
    filled_so_far: int,
    base_asset: str,
    result: OrderProcessingResult,
) -> OrderProcessingResult:
    """
    Вычисляет, сколько тикеров может быть заполнено в текущем ордере,
    и обновляет статусы ордеров.
    """
    need = current_order.qty - filled_so_far
    available = matching_order.qty - matching_order.filled
    assert matching_order.price is not None
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
        ticker_price = matching_order.price
    else:
        if (
            current_order.direction == OrderDirection.sell
            and current_order.price > matching_order.price
        ) or (
            current_order.direction == OrderDirection.buy
            and current_order.price < matching_order.price
        ):
            return result
        ticker_filled = min(need, available)
        ticker_price = matching_order.price
        matching_order.filled += ticker_filled
        if matching_order.filled < matching_order.qty:
            matching_order.status = OrderStatus.partially_executed
        else:
            matching_order.status = OrderStatus.executed

    return await update_result(
        current_order=current_order,
        matching_order=matching_order,
        ticker_filled=ticker_filled,
        ticker_price=ticker_price,
        base_asset=base_asset,
        result=result,
    )


async def update_current_order_status(
    current_order: Order, ticker_count: int
) -> UpdateOrder:
    """
    Обновляет статус текущего ордера на основе количества заполненных тикеров.
    """
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


async def processing_cancelled_order(
    updated_current_order: UpdateOrder,
    result: OrderProcessingResult,
):
    """
    Обрабатывает отмененный ордер, очищая предыдущие результаты
    и добавляя информацию о возврате средств.
    """
    result.clear_all()
    result.add_order(updated_current_order)
    result.status_code = 400
    result.detail = "Order cant execute"
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
    """
    Основная функция обработки списка ордеров.
    Последовательно обрабатывает каждый ордер из списка matching_orders.
    """
    result = OrderProcessingResult()
    for order in matching_orders:
        if result.ticker_count >= current_order.qty:
            break

        await calculate_order_fill(
            current_order=current_order,
            matching_order=order,
            filled_so_far=result.ticker_count,
            base_asset=base_asset,
            result=result,
        )

    updated_current_order = await update_current_order_status(
        current_order, result.ticker_count
    )
    if current_order.status == OrderStatus.cancelled:
        result = await processing_cancelled_order(
            updated_current_order=updated_current_order, result=result
        )
    elif current_order.filled > 0:
        result.add_order(updated_current_order)

    return result


async def update_orders(
    orders: list[UpdateOrder], order_repository: OrderRepository
) -> None:
    await order_repository.bulk_update(orders)


async def update_balances(
    result: OrderProcessingResult,
    balance_repository: BalanceRepository,
) -> None:
    await balance_repository.bulk_adjust(
        deposit_balances=result.deposit_balances,
        withdraw_balances=result.withdraw_balances,
    )


async def create_transactions(
    transactions: list[Transaction],
    transaction_repository: TransactionRepository,
) -> None:
    await transaction_repository.bulk_create(transactions)


async def process_order_fill(
    result: OrderProcessingResult,
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    balance_repository: BalanceRepository,
) -> None:
    """
    Применяет все изменения: обновляет ордера и балансы, создает транзакции.
    """
    if result.changed_orders:
        await update_orders(result.changed_orders, order_repository)
        logger.info(f"Update orders: {result.changed_orders}")

    if result.transactions:
        await create_transactions(result.transactions, transaction_repository)
        logger.info(f"Create transactions: {result.transactions}")
    if result.deposit_balances:
        await update_balances(result, balance_repository)
        logger.info(f"Deposit balances: {result.deposit_balances}")
        logger.info(f"Withdraw balances: {result.withdraw_balances}")


async def accept_or_deny_operation(
    current_order: Order,
    base_asset: str,
    result: OrderProcessingResult,
    balance_repository: BalanceRepository,
) -> OrderProcessingResult:
    """
    Проверяет, достаточно ли средств для выполнения ордера,
    и либо подтверждает, либо отклоняет операцию.
    """
    user_balance = await balance_repository.get_balance_by_user_id_and_ticker(
        current_order.user_id, base_asset
    )
    assert user_balance is not None
    if user_balance.qty - user_balance.reserve < result.final_cost:
        result.clear_all()
        result.add_order(
            UpdateOrder(
                id=current_order.id,
                filled=current_order.filled,
                status=OrderStatus.cancelled,
                price=current_order.price,
            )
        )
        result.status_code = 400
        result.detail = f"Недостаточно {base_asset} на балансе"
        logger.info(f"Operation denied: {result}")
    return result


async def check_and_reserve_balance(
    current_order: Order,
    base_asset: str,
    balance_repository: BalanceRepository,
) -> OrderFinalResult | None:
    """
    Проверяет баланс пользователя и резервирует средства для ордера.
    Возвращает ошибку, если средств недостаточно.
    """
    user_base_asset_balance = (
        await balance_repository.get_balance_by_user_id_and_ticker(
            current_order.user_id, base_asset
        )
    )
    user_current_ticker_balance = (
        await balance_repository.get_balance_by_user_id_and_ticker(
            current_order.user_id, current_order.ticker
        )
    )
    if current_order.direction == OrderDirection.sell:
        if user_current_ticker_balance is None:
            return OrderFinalResult(
                status_code=400,
                order_id=current_order.id,
                detail=f"{current_order.ticker} отсутствует на балансе",
            )
        elif user_current_ticker_balance.qty < current_order.qty:
            return OrderFinalResult(
                status_code=400,
                order_id=current_order.id,
                detail=f"Недостаточно {user_current_ticker_balance.ticker} на балансе",  # noqa
            )
        await balance_repository.reserve(
            Balance(
                user_id=current_order.user_id,
                ticker=current_order.ticker,
                reserve=current_order.qty,
            )
        )
    else:
        if user_base_asset_balance is None:
            return OrderFinalResult(
                status_code=400,
                order_id=current_order.id,
                detail=f"{base_asset} отсутствует на балансе",
            )
        elif current_order.price is not None:
            if (
                user_base_asset_balance.qty
                < current_order.price * current_order.qty
            ):
                return OrderFinalResult(
                    status_code=400,
                    order_id=current_order.id,
                    detail=f"Недостаточно {user_base_asset_balance.ticker} на балансе",  # noqa
                )
            await balance_repository.reserve(
                Balance(
                    user_id=current_order.user_id,
                    ticker=user_base_asset_balance.ticker,
                    reserve=current_order.price * current_order.qty,
                )
            )

    return None


async def process_order(
    current_order: Order,
    balance_repository: BalanceRepository,
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    app_config_repository: AppConfigRepository,
) -> OrderFinalResult:
    """
    Основная функция обработки ордера:
    1. Блокирует ресурсы
    2. Проверяет и резервирует баланс
    3. Находит совпадающие ордера
    4. Обрабатывает сделки
    5. Применяет изменения
    6. Разблокирует ресурсы
    """
    logger.info(f"New order received: {current_order}")
    order_lock_id = await order_repository.advisory_lock_by_ticker(
        current_order.ticker
    )
    logger.info(
        f"Order repository obtained advisory lock {order_lock_id}"
        f" by ticker {current_order.ticker}"
    )
    balance_lock_id = await balance_repository.advisory_lock_by_ticker(
        current_order.ticker
    )
    logger.info(
        f"Balance repository obtained advisory lock {balance_lock_id}"
        f" by ticker {current_order.ticker}"
    )

    base_asset = await app_config_repository.get("base_asset") or "RUB"
    not_enough_balance = await check_and_reserve_balance(
        current_order=current_order,
        base_asset=base_asset,
        balance_repository=balance_repository,
    )
    if not_enough_balance:
        return not_enough_balance

    try:
        await order_repository.create(current_order)

        logger.info(f"Process order has started: {current_order}")

        matching_orders = await get_matching_orders(
            current_order, order_repository
        )

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
            result=processing_result,
            order_repository=order_repository,
            transaction_repository=transaction_repository,
            balance_repository=balance_repository,
        )
        return OrderFinalResult(
            status_code=processing_result.status_code,
            order_id=current_order.id,
            detail=processing_result.detail,
        )
    except Exception as error:
        logger.error(f"Order failed: {current_order}, {error}", exc_info=True)
        return OrderFinalResult(
            status_code=500,
            order_id=current_order.id,
            detail="Internal server error",
        )
    finally:
        await balance_repository.advisory_unlock(balance_lock_id)
        logger.info(
            f"Balance repository removed advisory lock {balance_lock_id}"
            f" by ticker {current_order.ticker}"
        )
        await order_repository.advisory_unlock(order_lock_id)
        logger.info(
            f"Order repository removed advisory lock {order_lock_id}"
            f" by ticker {current_order.ticker}"
        )
