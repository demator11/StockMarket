from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.models.database_models.balance import Balance
from application.models.database_models.user import UserRole
from application.models.endpoint_models.balance.deposit_balance import (
    DepositUserBalanceRequest,
)
from application.models.endpoint_models.balance.withdraw_balance import (
    WithdrawBalanceRequest,
)
from application.models.endpoint_models.intrument.create_instrument import (
    CreateInstrumentRequest,
)
from application.models.endpoint_models.success_response import (
    SuccessResponse,
)
from application.database.repository.user_repository import UserRepository
from application.database.repository.instrument_repository import (
    InstrumentRepository,
)
from application.di.repositories import (
    get_instrument_repository,
    get_user_repository,
    get_balance_repository,
)
from application.models.database_models.instrument import Instrument
from application.token_management import (
    admin_authorization,
    user_authorization,
)


admin_router = APIRouter(prefix="/api/v1/admin")


@admin_router.post("/instrument")
async def add_instrument(
    new_instrument: CreateInstrumentRequest,
    authorization: UUID = Depends(admin_authorization),
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
) -> SuccessResponse:
    instrument = Instrument(
        name=new_instrument.name, ticker=new_instrument.ticker
    )
    ticker_exists = await instrument_repository.exists_in_database(
        instrument.ticker
    )
    if ticker_exists:
        raise HTTPException(status_code=400, detail="Тикер уже существует")
    await instrument_repository.create(instrument)
    return SuccessResponse()


@admin_router.delete("/instrument/{ticker}")
async def delete_instrument(
    ticker: str,
    authorization: UUID = Depends(admin_authorization),
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
) -> SuccessResponse:
    ticker_exists = await instrument_repository.exists_in_database(ticker)
    if not ticker_exists:
        raise HTTPException(status_code=404, detail="Тикер не найден")

    await instrument_repository.delete(ticker)
    return SuccessResponse()


@admin_router.post("/balance/deposit", summary="Deposit")
async def deposit_balance(
    deposit: DepositUserBalanceRequest,
    authorization: UUID = Depends(admin_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> SuccessResponse:
    deposit = Balance(
        user_id=deposit.user_id, ticker=deposit.ticker, qty=deposit.amount
    )
    await balance_repository.upsert(deposit)
    return SuccessResponse()


@admin_router.post("/balance/withdraw", summary="Withdraw")
def withdraw_balance(
    body: WithdrawBalanceRequest,
    authorization: UUID = Depends(admin_authorization),
) -> SuccessResponse:
    # пытаемся вывести коины с баланса юзера
    return SuccessResponse()


@admin_router.get("/")
async def get_admin_role(
    authorization: UUID = Depends(user_authorization),
    user_repository: UserRepository = Depends(get_user_repository),
):
    await user_repository.change_user_role(authorization, UserRole.admin)
    return SuccessResponse()
