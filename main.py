# import uvicorn
# from fastapi import FastAPI
#
# from routers.public import router_public
# from routers.balance import router_balance
# from routers.order import router_order
# from routers.admin import router_admin
#
#
# app = FastAPI()
# app.include_router(router_public, tags=["public"])
# app.include_router(router_balance, tags=["balance"])
# app.include_router(router_order, tags=["order"])
# app.include_router(router_admin, tags=["admin"])
# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)

from database.orm import AsyncORM
import asyncio


def main():
    AsyncORM.migration()


if __name__ == "__main__":
    main()
