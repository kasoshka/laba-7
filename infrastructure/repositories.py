from typing import Dict, Optional
from domain.order import Order
from application.use_cases import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def save(self, order: Order):
        self._orders[order.id] = order
