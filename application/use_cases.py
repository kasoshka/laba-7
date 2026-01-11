from abc import ABC, abstractmethod
from typing import Optional
from domain.order import Order
from domain.value_objects import Money
from dataclasses import dataclass
from typing import Tuple
from domain.order import Order
from domain.value_objects import Money
from .interfaces import OrderRepository, PaymentGateway

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


@dataclass
class PaymentResult:
    success: bool
    message: str
    order_id: str


class PayOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        payment_gateway: PaymentGateway
    ):
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway

    def execute(self, order_id: str) -> PaymentResult:
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return PaymentResult(
                success=False,
                message=f"Order {order_id} not found",
                order_id=order_id
            )

        try:
            order.pay()
            
            payment_success = self.payment_gateway.charge(order_id, order.total)
            
            if payment_success:
                self.order_repository.save(order)
                return PaymentResult(
                    success=True,
                    message="Payment successful",
                    order_id=order_id
                )
            else:
                order.status = OrderStatus.PENDING
                return PaymentResult(
                    success=False,
                    message="Payment gateway failed",
                    order_id=order_id
                )
                
        except ValueError as e:
            return PaymentResult(
                success=False,
                message=str(e),
                order_id=order_id
            )
