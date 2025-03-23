from uuid import UUID

from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Depends

from application.models.enum_models.user import UserRole
from application.models.endpoint_models.instrument import (
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
    check_ticker_exists = await instrument_repository.exists_in_database(
        instrument.ticker
    )
    if check_ticker_exists is True:
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
    check_ticker_exists = await instrument_repository.exists_in_database(
        ticker
    )
    if check_ticker_exists is False:
        raise HTTPException(status_code=404, detail="Тикер не найден")

    await instrument_repository.delete(ticker)
    return SuccessResponse()


@admin_router.get("/")
async def get_admin_role(
    authorization: UUID = Depends(user_authorization),
    user_repository: UserRepository = Depends(get_user_repository),
):
    await user_repository.change_user_role(authorization, UserRole.admin)
    return SuccessResponse()
