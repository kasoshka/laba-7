from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from uuid import uuid4
from .value_objects import Money, OrderStatus


@dataclass
class OrderLine:
    product_id: str
    product_name: str
    price: Money
    quantity: int

    @property
    def total(self) -> Money:
        return Money(self.price.amount * self.quantity, self.price.currency)


class Order:
    def __init__(self, customer_id: str):
        self.id = str(uuid4())
        self.customer_id = customer_id
        self.status = OrderStatus.PENDING
        self.lines: List[OrderLine] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self._paid_at: Optional[datetime] = None

    def add_line(self, line: OrderLine):
        if self.status == OrderStatus.PAID:
            raise ValueError("Cannot modify paid order")
        self.lines.append(line)
        self.updated_at = datetime.now()

    def remove_line(self, product_id: str):
        if self.status == OrderStatus.PAID:
            raise ValueError("Cannot modify paid order")
        self.lines = [line for line in self.lines if line.product_id != product_id]
        self.updated_at = datetime.now()

    @property
    def total(self) -> Money:
        if not self.lines:
            return Money(0)
        
        total = self.lines[0].total
        for line in self.lines[1:]:
            total += line.total
        return total

    def pay(self):
        """Доменная операция оплаты заказа"""
        if not self.lines:
            raise ValueError("Cannot pay empty order")
        
        if self.status == OrderStatus.PAID:
            raise ValueError("Order already paid")
        
        self.status = OrderStatus.PAID
        self._paid_at = datetime.now()
        self.updated_at = datetime.now()

    @property
    def is_paid(self) -> bool:
        return self.status == OrderStatus.PAID

    @property
    def paid_at(self) -> Optional[datetime]:
        return self._paid_at
