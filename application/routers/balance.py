from uuid import UUID
from fastapi import APIRouter, Depends

from application.models.endpoint_models.success_response import (
    SuccessResponse,
)
from application.models.endpoint_models.body_deposit import (
    CreateBodyDepositRequest,
)
from application.models.endpoint_models.body_withdraw import (
    CreateBodyWithdrawRequest,
)
from application.models.database_models.deposit import NewDeposit, Deposit
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
):
    result = await balance_repository.get_user_by_id(authorization)
    balance_dict = {}
    for row in result:
        balance_dict[row.ticker] = row.qty
    return balance_dict


@balance_router.post("/deposit", summary="Deposit")
async def deposit_balance(
    deposit: CreateBodyDepositRequest,
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> SuccessResponse:
    deposit = Deposit(
        user_id=authorization, ticker=deposit.ticker, qty=deposit.amount
    )
    await balance_repository.upsert_user_deposit(deposit)
    return SuccessResponse()


@balance_router.post("/withdraw", summary="Withdraw")
def create_withdraw(
    body: CreateBodyWithdrawRequest,
    authorization: UUID = Depends(user_authorization),
) -> SuccessResponse:
    # пытаемся вывести коины с баланса юзера
    return SuccessResponse()
