import unittest
from domain.order import Order, OrderLine
from domain.value_objects import Money, OrderStatus
from infrastructure.repositories import InMemoryOrderRepository
from infrastructure.payment_gateways import FakePaymentGateway
from application.use_cases import PayOrderUseCase


class TestPayOrderUseCase(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryOrderRepository()
        self.payment_gateway = FakePaymentGateway()
        self.use_case = PayOrderUseCase(self.repository, self.payment_gateway)

    def create_order_with_lines(self):
        order = Order(customer_id="customer_123")
        order.add_line(OrderLine(
            product_id="prod_1",
            product_name="Product 1",
            price=Money(100),
            quantity=2
        ))
        order.add_line(OrderLine(
            product_id="prod_2",
            product_name="Product 2",
            price=Money(50),
            quantity=1
        ))
        self.repository.save(order)
        return order

    def test_successful_payment(self):
        """Тест успешной оплаты корректного заказа"""
        order = self.create_order_with_lines()
        
        result = self.use_case.execute(order.id)
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Payment successful")
        
        # Проверяем, что заказ сохранен с правильным статусом
        saved_order = self.repository.get_by_id(order.id)
        self.assertEqual(saved_order.status, OrderStatus.PAID)
        self.assertIsNotNone(saved_order.paid_at)
        
        # Проверяем корректный расчет суммы
        self.assertEqual(saved_order.total, Money(250))

    def test_payment_empty_order(self):
        """Тест ошибки при оплате пустого заказа"""
        order = Order(customer_id="customer_123")
        self.repository.save(order)
        
        result = self.use_case.execute(order.id)
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Cannot pay empty order")
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_double_payment_error(self):
        """Тест ошибки при повторной оплате"""
        order = self.create_order_with_lines()
        
        # Первая оплата
        result1 = self.use_case.execute(order.id)
        self.assertTrue(result1.success)
        
        # Вторая оплата
        result2 = self.use_case.execute(order.id)
        self.assertFalse(result2.success)
        self.assertEqual(result2.message, "Order already paid")

    def test_cannot_modify_after_payment(self):
        """Тест невозможности изменения заказа после оплаты"""
        order = self.create_order_with_lines()
        
        # Оплачиваем заказ
        result = self.use_case.execute(order.id)
        self.assertTrue(result.success)
        
        # Пытаемся добавить строку после оплаты
        with self.assertRaises(ValueError) as context:
            order.add_line(OrderLine(
                product_id="prod_3",
                product_name="Product 3",
                price=Money(200),
                quantity=1
            ))
        self.assertIn("Cannot modify paid order", str(context.exception))

    def test_total_calculation(self):
        """Тест корректного расчета итоговой суммы"""
        order = Order(customer_id="customer_123")
        order.add_line(OrderLine(
            product_id="prod_1",
            product_name="Product 1",
            price=Money(100),
            quantity=3
        ))
        order.add_line(OrderLine(
            product_id="prod_2",
            product_name="Product 2",
            price=Money(150.50),
            quantity=2
        ))
        
        # 100 * 3 + 150.50 * 2 = 300 + 301 = 601
        expected_total = Money(601.0)
        self.assertEqual(order.total, expected_total)


if __name__ == '__main__':
    unittest.main()
