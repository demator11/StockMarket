from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.models.database_models.balance import Balance
from application.models.database_models.user import UserRole
from application.models.endpoint_models.admin.create_instrument import (
    CreateInstrumentRequest,
)
from application.models.endpoint_models.admin.delete_user import (
    DeleteUserResponse,
)
from application.models.endpoint_models.balance.deposit_balance import (
    DepositUserBalanceRequest,
)
from application.models.endpoint_models.balance.withdraw_balance import (
    WithdrawUserBalanceRequest,
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


@admin_router.delete("/user/{user_id}")
async def delete_user(
    user_id: UUID,
    authorization: UUID = Depends(admin_authorization),
    user_repository: UserRepository = Depends(get_user_repository),
) -> DeleteUserResponse:
    deleted_user = await user_repository.delete(user_id)
    if deleted_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    return DeleteUserResponse(
        id=deleted_user.id,
        name=deleted_user.name,
        role=deleted_user.role,
        api_key=deleted_user.api_key,
    )


@admin_router.post("/instrument")
async def create_instrument(
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
async def deposit_user_balance(
    deposit_request: DepositUserBalanceRequest,
    authorization: UUID = Depends(admin_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> SuccessResponse:
    deposit = Balance(
        user_id=deposit_request.user_id,
        ticker=deposit_request.ticker,
        qty=deposit_request.amount,
    )
    await balance_repository.upsert(deposit)
    return SuccessResponse()


@admin_router.post("/balance/withdraw", summary="Withdraw")
async def withdraw_user_balance(
    withdraw_request: WithdrawUserBalanceRequest,
    authorization: UUID = Depends(admin_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> SuccessResponse:
    withdraw = Balance(
        user_id=withdraw_request.user_id,
        ticker=withdraw_request.ticker,
        qty=withdraw_request.amount,
    )
    result = await balance_repository.delete_or_update(withdraw)
    if result is None:
        raise HTTPException(
            status_code=400, detail="У пользователя отсутствует данный тикер"
        )
    return SuccessResponse()


@admin_router.post("/")
async def get_admin_role(
    authorization: UUID = Depends(user_authorization),
    user_repository: UserRepository = Depends(get_user_repository),
):
    await user_repository.change_user_role(authorization, UserRole.admin)
    return SuccessResponse()
