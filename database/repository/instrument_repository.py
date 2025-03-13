from sqlalchemy import insert, select

from models.instrument import Instrument
from database.database_models.instrument import InstrumentOrm
from database.engine import async_session_factory


class InstrumentRepository:
    @staticmethod
    async def create_instrument(new_instrument: Instrument) -> Instrument:
        async with async_session_factory.begin() as session:
            result = await session.scalars(
                insert(InstrumentOrm)
                .values(
                    name=new_instrument.name,
                    ticker=new_instrument.ticker,
                )
                .returning(InstrumentOrm)
            )
            return Instrument.from_orm(result.one())

    @staticmethod
    async def check_has_in_database(ticker: str) -> bool:
        async with async_session_factory() as session:
            query = select(InstrumentOrm.ticker).filter(
                InstrumentOrm.ticker == ticker
            )
            result = await session.execute(query)
            if result.first() is None:
                return False
            return True

    @staticmethod
    async def get_instrument_list():
        async with async_session_factory() as session:
            query = select(InstrumentOrm)
            result = await session.execute(query)
            return [Instrument.from_orm(x) for x in result.scalars().all()]
