from enum import StrEnum


class OrderDirection(StrEnum):
    buy = "BUY"
    sell = "SELL"


class OrderStatus(StrEnum):
    new = "NEW"
    executed = "EXECUTED"
    partially_executed = "PARTIALLY_EXECUTED"
    cancelled = "CANCELLED"
