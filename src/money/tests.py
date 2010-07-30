from decimal import Decimal
import unittest

from Money import Currency, Money, CURRENCIES, set_default_currency


class TestCurrency(unittest.TestCase):

    def setUp(self):
	self.default_curr_code = 'XYZ'
	self.default_curr = CURRENCIES[self.default_curr_code]

    def test_init(self):
	usd_countries = CURRENCIES['USD'].countries
	US_dollars = Currency(code='USD', numeric='840', name='US Dollar', countries=['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY', 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA', 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO', 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES MINOR OUTLYING ISLANDS', 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
	self.assertEqual(US_dollars.code, 'USD')
	self.assertEqual(US_dollars.numeric, '840')
	self.assertEqual(US_dollars.name, 'US Dollar')
	self.assertEqual(US_dollars.countries, usd_countries)

    def test_repr(self):
	self.assertEqual(str(self.default_curr), self.default_curr_code)

    def test_set_exchange_rate(self):
	test_exch_rate = Decimal('1.23')
	self.default_curr.set_exchange_rate(test_exch_rate)
	self.assertEqual(self.default_curr.exchange_rate, test_exch_rate) 


class TestMoney(unittest.TestCase):

    def setUp(self):
	self.one_million_decimal = Decimal('1000000')
	self.USD = CURRENCIES['USD']

    def test_init(self):
	one_million = self.one_million_decimal
	one_million_dollars = Money(amount=one_million, currency=self.USD)
	self.assertEqual(one_million_dollars.amount, one_million)
	self.assertEqual(one_million_dollars.currency, self.USD)

    def test_init_string_currency_code(self):
	one_million = self.one_million_decimal
	one_million_dollars = Money(amount=one_million, currency='usd')
	self.assertEqual(one_million_dollars.amount, one_million)
	self.assertEqual(one_million_dollars.currency, self.USD)

    def test_init_default_currency(self):
	one_million = self.one_million_decimal
	set_default_currency(code='USD')  # Changes global default currency.
	one_million_dollars = Money(amount=one_million)  # No currency given.
	self.assertEqual(one_million_dollars.amount, one_million)
	self.assertEqual(one_million_dollars.currency, self.USD)

    def test_init_float(self):
	one_million_dollars = Money(amount=1000000.0)
	self.assertEqual(one_million_dollars.amount, self.one_million_decimal)

    def test_repr(self):
	one_million_dollars = Money(amount=self.one_million_decimal, currency=self.USD)
	self.assertEqual(str(one_million_dollars), 'USD 1000000.00')



if __name__ == '__main__':
    unittest.main()
