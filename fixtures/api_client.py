import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from application.routers.admin import admin_router
from application.routers.balance import balance_router
from application.routers.order import order_router
from application.routers.public import public_router

# @pytest.fixture
# def app():
#     app = FastAPI()
#     app.include_router(public_router, tags=["public"])
#     app.include_router(balance_router, tags=["balance"])
#     app.include_router(order_router, tags=["order"])
#     app.include_router(admin_router, tags=["admin"])
#     return app


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client(db_session):
    app = FastAPI()
    app.include_router(public_router, tags=["public"])
    app.include_router(balance_router, tags=["balance"])
    app.include_router(order_router, tags=["order"])
    app.include_router(admin_router, tags=["admin"])

    # app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as c:
        yield c
