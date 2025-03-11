from typing import Annotated
from fastapi import APIRouter, Header

from models.instrument import Instrument
from models.ok import Ok

router_admin = APIRouter()


@router_admin.post("/api/v1/admin/instrument")
def add_instrument(
    instrument: Instrument,
    authorization: Annotated[str | None, Header()] = None,
) -> Ok:
    # добавляем инструмент
    return Ok()


@router_admin.delete("/api/v1/admin/instrument/{ticker}")
def delete_instrument(
    ticker: str, authorization: Annotated[str | None, Header()] = None
) -> Ok:
    # удаляем инструмент
    return Ok()
