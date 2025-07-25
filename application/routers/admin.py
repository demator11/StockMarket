from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from application.database.repository.app_config_repository import (
    AppConfigRepository,
)
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.models.database_models.app_config import AppConfig
from application.models.database_models.balance import Balance
from application.models.endpoint_models.admin.create_config import (
    CreateConfigRequest,
)
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
    get_app_config_repository,
)
from application.models.database_models.instrument import Instrument
from application.token_management import (
    admin_authorization,
)


admin_router = APIRouter(prefix="/api/v1/admin")


@admin_router.delete("/user/{user_id}")
async def delete_user(
    user_id: UUID,
    authorization: UUID = Depends(admin_authorization),
    user_repository: UserRepository = Depends(get_user_repository),
) -> DeleteUserResponse:
    """
    Удаляет пользователя по его ID
    """
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
    """
    Создаёт новый инструмент
    """
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
    """
    Удаляет существующий инструмент
    """
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
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
    user_repository: UserRepository = Depends(get_user_repository),
) -> SuccessResponse:
    """
    Пополняет баланс пользователя
    """
    deposit = Balance(
        user_id=deposit_request.user_id,
        ticker=deposit_request.ticker,
        qty=deposit_request.amount,
    )
    user_exists = await user_repository.exists_id_in_database(deposit.user_id)
    if not user_exists:
        raise HTTPException(
            status_code=400, detail="Данного пользователя не существует"
        )

    ticker_exists = await instrument_repository.exists_in_database(
        deposit.ticker
    )
    if not ticker_exists:
        raise HTTPException(
            status_code=400, detail="Данного тикера не существует"
        )
    await balance_repository.upsert(deposit)
    return SuccessResponse()


@admin_router.post("/balance/withdraw", summary="Withdraw")
async def withdraw_user_balance(
    withdraw_request: WithdrawUserBalanceRequest,
    authorization: UUID = Depends(admin_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> SuccessResponse:
    """
    Снимает инструменты с баланса пользователя
    """
    withdraw = Balance(
        user_id=withdraw_request.user_id,
        ticker=withdraw_request.ticker,
        qty=withdraw_request.amount,
    )
    user_exists = await user_repository.exists_id_in_database(withdraw.user_id)
    if not user_exists:
        raise HTTPException(
            status_code=400, detail="Данного пользователя не существует"
        )
    result = await balance_repository.withdraw(withdraw)
    if result is None:
        raise HTTPException(
            status_code=400, detail="У пользователя отсутствует данный тикер"
        )
    return SuccessResponse()


@admin_router.post("/config/create")
async def create_config(
    new_config: CreateConfigRequest,
    authorization: UUID = Depends(admin_authorization),
    config_repository: AppConfigRepository = Depends(
        get_app_config_repository
    ),
) -> SuccessResponse:
    """
    Создаёт новый, либо изменяет старый конфиг
    """
    config = AppConfig(key=new_config.key, value=new_config.value)
    await config_repository.upsert(config)
    return SuccessResponse()
