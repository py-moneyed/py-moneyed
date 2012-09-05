import unittest


class TestMoney(unittest.TestCase):

    def create_instance(self, amount=0.0, currency='EUR'):
        from decimal import Decimal
        from moneyed.classes import Money
        return Money(amount=Decimal(amount), currency=currency)

    def test_subclass(self):
        from moneyed.classes import Money
        self.assertTrue(issubclass(Money, object))

    def test_instance(self):
        from moneyed.classes import Money
        instance = self.create_instance()
        self.assertIsInstance(instance, Money)

