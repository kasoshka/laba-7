from domain.value_objects import Money
from application.use_cases import PaymentGateway


class FakePaymentGateway(PaymentGateway):
    def __init__(self, always_succeed: bool = True):
        self.always_succeed = always_succeed
        self.charges_made = []

    def charge(self, order_id: str, amount: Money) -> bool:
        self.charges_made.append({
            'order_id': order_id,
            'amount': amount
        })
        return self.always_succeed
