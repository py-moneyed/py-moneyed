from moneyed.classes import Currency

import unittest


class TestCurrency(unittest.TestCase):

    def test_subclass(self):
        self.assertTrue(issubclass(Currency, object))

    def test_instance(self):
        instance = Currency()
        self.assertIsInstance(instance, Currency)

    def test_code_default(self):
        instance = Currency()
        self.assertEqual(instance.code, '')

    def test_code(self):
        instance = Currency(code='EUR')
        self.assertEqual(instance.code, 'EUR')

    def test_numeric_default(self):
        instance = Currency()
        self.assertEqual(instance.numeric, '999')

    def test_numeric(self):
        instance = Currency(numeric='888')
        self.assertEqual(instance.numeric, '888')

    def test_name_default(self):
        instance = Currency()
        self.assertEqual(instance.name, '')

    def test_name(self):
        instance = Currency(name='Euro')
        self.assertEqual(instance.name, 'Euro')

    def test_countries_default(self):
        instance = Currency()
        self.assertEqual(instance.countries, [])

    def test_countries(self):
        instance = Currency(countries=['Finland'])
        self.assertEqual(instance.countries, ['Finland'])

    def test___repr__(self):
        instance = Currency(code='EUR')
        self.assertEqual(instance.__repr__(), 'EUR')

    def test___eq__(self):
        currency1 = Currency()
        currency2 = Currency()
        self.assertEqual(currency1, currency2)
