#file test_moneyed_classes.py
from copy import deepcopy
from decimal import Decimal
import pytest  # Works with less code, more consistency than unittest.

from moneyed.classes import Currency, Money, MoneyComparisonError, CURRENCIES, DEFAULT_CURRENCY
from moneyed.localization import format_money


class TestCurrency:

    def setup_method(self, method):
        self.default_curr_code = 'XYZ'
        self.default_curr = CURRENCIES[self.default_curr_code]

    def test_init(self):
        usd_countries = CURRENCIES['USD'].countries
        US_dollars = Currency(code='USD', numeric='840', name='US Dollar', countries=['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY', 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA', 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO', 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES MINOR OUTLYING ISLANDS', 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
        assert US_dollars.code == 'USD'
        assert US_dollars.countries == usd_countries
        assert US_dollars.name == 'US Dollar'
        assert US_dollars.numeric == '840'

    def test_repr(self):
        assert str(self.default_curr) == self.default_curr_code

    def test_compare(self):
        other = deepcopy(self.default_curr)
        # equality
        assert self.default_curr == CURRENCIES['XYZ']
        assert self.default_curr == other
        # non-equality
        other.code = 'USD'
        assert self.default_curr != other
        assert self.default_curr != CURRENCIES['USD']


class TestMoney:

    def setup_method(self, method):
        self.one_million_decimal = Decimal('1000000')
        self.USD = CURRENCIES['USD']
        self.one_million_bucks = Money(amount=self.one_million_decimal,
                                       currency=self.USD)

    def test_init(self):
        one_million_dollars = Money(amount=self.one_million_decimal,
                                    currency=self.USD)
        assert one_million_dollars.amount == self.one_million_decimal
        assert one_million_dollars.currency == self.USD

    def test_init_string_currency_code(self):
        one_million_dollars = Money(amount=self.one_million_decimal,
                                    currency='usd')
        assert one_million_dollars.amount == self.one_million_decimal
        assert one_million_dollars.currency == self.USD

    def test_init_default_currency(self):
        one_million = self.one_million_decimal
        one_million_dollars = Money(amount=one_million)  # No currency given!
        assert one_million_dollars.amount == one_million
        assert one_million_dollars.currency == DEFAULT_CURRENCY

    def test_init_float(self):
        one_million_dollars = Money(amount=1000000.0)
        assert one_million_dollars.amount == self.one_million_decimal

    def test_repr(self):
        assert repr(self.one_million_bucks) == '1000000 USD'
        assert repr(Money(Decimal('2.000'), 'PLN')) == '2 PLN'

    def test_str(self):
        assert str(self.one_million_bucks) == 'US$1,000,000.00'

    def test_format_money(self):
        # Two decimal places by default
        assert format_money(self.one_million_bucks) == 'US$1,000,000.00'
        # No decimal point without fractional part
        assert format_money(self.one_million_bucks, decimal_places=0) == 'US$1,000,000'

    def test_add(self):
        assert (self.one_million_bucks + self.one_million_bucks
                == Money(amount='2000000', currency=self.USD))

    def test_add_non_money(self):
        with pytest.raises(TypeError):
            Money(1000) + 123

    def test_sub(self):
        zeroed_test = self.one_million_bucks - self.one_million_bucks
        assert zeroed_test == Money(amount=0, currency=self.USD)

    def test_sub_non_money(self):
        with pytest.raises(TypeError):
            Money(1000) - 123

    def test_mul(self):
        x = Money(amount=111.33, currency=self.USD)
        assert 3 * x == Money(333.99, currency=self.USD)
        assert Money(333.99, currency=self.USD) == 3 * x

    def test_mul_bad(self):
        with pytest.raises(TypeError):
            self.one_million_bucks * self.one_million_bucks

    def test_div(self):
        x = Money(amount=50, currency=self.USD)
        y = Money(amount=2, currency=self.USD)
        assert x / y == Decimal(25)

    def test_div_mismatched_currencies(self):
        x = Money(amount=50, currency=self.USD)
        y = Money(amount=2, currency=CURRENCIES['CAD'])
        with pytest.raises(TypeError):
            assert x / y == Money(amount=25, currency=self.USD)

    def test_div_by_non_Money(self):
        x = Money(amount=50, currency=self.USD)
        y = 2
        assert x / y == Money(amount=25, currency=self.USD)

    def test_rmod(self):
        assert 1 % self.one_million_bucks == Money(amount=10000,
                                                   currency=self.USD)

    def test_rmod_bad(self):
        with pytest.raises(TypeError):
            assert (self.one_million_bucks % self.one_million_bucks
                    == 1)

    def test_convert_to_default(self):
        # Currency conversions are not implemented as of 2/2011; when
        # they are working, then convert_to_default and convert_to
        # will need to be tested.
        pass

    # Note: no tests for __eq__ as it's quite thoroughly covered in
    # the assert comparisons throughout these tests.

    def test_ne(self):
        x = Money(amount=1, currency=self.USD)
        assert self.one_million_bucks != x

    def test_equality_to_other_types(self):
        x = Money(amount=1, currency=self.USD)
        assert self.one_million_bucks != None
        assert self.one_million_bucks != {}

    def test_not_equal_to_decimal_types(self):
        assert self.one_million_bucks != self.one_million_decimal

    def test_lt(self):
        x = Money(amount=1, currency=self.USD)
        assert x < self.one_million_bucks

    def test_lt_mistyped(self):
        x = 1.0
        with pytest.raises(MoneyComparisonError):
            assert x < self.one_million_bucks

    def test_gt(self):
        x = Money(amount=1, currency=self.USD)
        assert self.one_million_bucks > x

    def test_gt_mistyped(self):
        x = 1.0
        with pytest.raises(MoneyComparisonError):
            assert self.one_million_bucks > x
