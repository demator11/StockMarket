from uuid import UUID
from fastapi import APIRouter, Depends

from application.models.endpoint_models.success_response import (
    SuccessResponse,
)
from application.models.endpoint_models.balance.deposit_balance import (
    DepositBalanceRequest,
)
from application.models.endpoint_models.balance.withdraw_balance import (
    WithdrawBalanceRequest,
)
from application.models.database_models.deposit import Deposit
from application.token_management import user_authorization
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.di.repositories import get_balance_repository

balance_router = APIRouter(prefix="/api/v1/balance")


@balance_router.get("/", summary="Get Balance")
async def get_balance(
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> dict:
    result = await balance_repository.get_user_by_id(authorization)
    return {row.ticker: row.qty for row in result}


@balance_router.post("/deposit", summary="Deposit")
async def deposit_balance(
    deposit: DepositBalanceRequest,
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> SuccessResponse:
    deposit = Deposit(
        user_id=authorization, ticker=deposit.ticker, qty=deposit.amount
    )
    await balance_repository.upsert_user_deposit(deposit)
    return SuccessResponse()


@balance_router.post("/withdraw", summary="Withdraw")
def withdraw_balance(
    body: WithdrawBalanceRequest,
    authorization: UUID = Depends(user_authorization),
) -> SuccessResponse:
    # пытаемся вывести коины с баланса юзера
    return SuccessResponse()
