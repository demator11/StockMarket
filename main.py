import uvicorn
from fastapi import FastAPI

from application.routers.public import public_router
from application.routers.balance import balance_router
from application.routers.order import order_router
from application.routers.admin import admin_router


app = FastAPI()
app.include_router(public_router, tags=["public"])
app.include_router(balance_router, tags=["balance"])
app.include_router(order_router, tags=["order"])
app.include_router(admin_router, tags=["admin"])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
#
# from database.orm import AsyncORM
# import asyncio
#
#
# async def main():
#     await AsyncORM.migration()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
