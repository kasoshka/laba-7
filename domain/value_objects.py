from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Currency:
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = Currency.RUB

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.currency not in [Currency.USD, Currency.EUR, Currency.RUB]:
            raise ValueError(f"Invalid currency: {self.currency}")

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
