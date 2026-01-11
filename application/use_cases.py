from abc import ABC, abstractmethod
from typing import Optional
from domain.order import Order
from domain.value_objects import Money


class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        pass

    @abstractmethod
    def save(self, order: Order):
        pass


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, order_id: str, amount: Money) -> bool:
        pass
