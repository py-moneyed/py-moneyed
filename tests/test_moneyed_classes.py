import warnings
from copy import deepcopy
from decimal import Decimal

import pytest  # Works with less code, more consistency than unittest.
from babel.core import get_global

from moneyed.classes import (
    CURRENCIES,
    USD,
    Currency,
    Money,
    MoneyComparisonError,
    force_decimal,
    get_currencies_of_country,
    get_currency,
    list_all_currencies,
)


class CustomDecimal(Decimal):
    """Test class to ensure Decimal.__str__ is not
    used in calculations.
    """

    def __str__(self):
        return "error"


class CustomClassAdd:
    """Test class to ensure Money.__add__(other) work properly if __radd__ is
    implemented for other"""

    def __add__(self, other):
        return "ok"

    def __radd__(self, other):
        return self.__add__(other)


class TestCurrency:
    def setup_method(self, method):
        self.code = "CHF"
        self.instance = CURRENCIES[self.code]

    def test_init(self):
        US_dollars = Currency(
            code="USD",
            numeric="840",
            sub_unit=100,
            name="United States Dollar",  # NB deliberately not official name
            countries=["UNITED STATES"],
        )
        assert US_dollars.code == "USD"
        assert US_dollars.countries == ["UNITED STATES"]
        assert US_dollars.name == "United States Dollar"
        assert US_dollars.numeric == "840"
        assert US_dollars.sub_unit == 100

    def test_name(self):
        assert USD.name == "US Dollar"

    def test_countries(self):
        assert CURRENCIES["AED"].countries == ["UNITED ARAB EMIRATES"]

    def test_get_name(self):
        assert USD.get_name("es") == "dólar estadounidense"
        assert USD.get_name("en_GB", count=10) == "US dollars"

    def test_repr(self):
        assert str(self.instance) == self.code

    def test_hash(self):
        assert self.instance in {self.instance}

    def test_compare(self):
        other = deepcopy(self.instance)
        # equality
        assert self.instance == CURRENCIES["CHF"]
        assert self.instance == other
        # non-equality
        other.code = "USD"
        assert self.instance != other
        assert self.instance != CURRENCIES["USD"]

    def test_fetching_currency_by_iso_code(self):
        assert get_currency("USD") == USD
        assert get_currency(iso="840") == USD
        assert get_currency(iso=840) == USD

    def test_get_currencies_of_country(self):
        assert get_currencies_of_country("IN")[0] == Currency("INR")
        assert get_currencies_of_country("iN")[0] == Currency("INR")
        assert get_currencies_of_country("BT") == [Currency("BTN"), Currency("INR")]
        assert get_currencies_of_country("XX") == []

    def test_zero_property(self):
        assert USD.zero == Money(0, "USD")
        assert USD.zero is USD.zero
        assert CURRENCIES["SEK"].zero == Money(0, "SEK")


class TestMoney:
    def setup_method(self, method):
        self.one_million_decimal = Decimal("1000000")
        self.USD = CURRENCIES["USD"]
        self.one_million_bucks = Money(
            amount=self.one_million_decimal, currency=self.USD
        )

    def test_init(self):
        one_million_dollars = Money(amount=self.one_million_decimal, currency=self.USD)
        assert one_million_dollars.amount == self.one_million_decimal
        assert one_million_dollars.currency == self.USD

    def test_init_string_currency_code(self):
        one_million_dollars = Money(amount=self.one_million_decimal, currency="usd")
        assert one_million_dollars.amount == self.one_million_decimal
        assert one_million_dollars.currency == self.USD

    def test_init_omit_currency(self):
        with pytest.raises(
            TypeError,
            match=r"__init__\(\) missing 1 required positional argument: 'currency'",
        ):
            Money(amount=self.one_million_decimal)

    def test_init_float(self):
        one_million_dollars = Money(amount=1000000.0, currency="PEN")
        assert one_million_dollars.amount == self.one_million_decimal

    def test_repr(self):
        assert repr(self.one_million_bucks) == "Money('1000000', 'USD')"
        assert repr(Money(Decimal("2.000"), "PLN")) == "Money('2.000', 'PLN')"
        m_1 = Money(Decimal("2.00"), "PLN")
        m_2 = Money(Decimal("2.01"), "PLN")
        assert repr(m_1) != repr(m_2)

    def test_eval_from_repr(self):
        m = Money("1000", "USD")
        assert m == eval(repr(m))

    def test_str(self):
        # Conversion to text use default locale, so results vary
        # depending on system setup. Just assert that we don't crash.
        assert isinstance(str(self.one_million_bucks), str)

    def test_hash(self):
        assert self.one_million_bucks in {self.one_million_bucks}

    def test_add(self):
        assert self.one_million_bucks + self.one_million_bucks == Money(
            amount="2000000", currency=self.USD
        )

    def test_add_non_money(self):
        with pytest.raises(TypeError):
            Money(1000) + 123

    def test_add_with_custom_class_add(self):
        custom_class_add = CustomClassAdd()
        assert Money(1000, "SOS") + custom_class_add == "ok"

    def test_sub(self):
        zeroed_test = self.one_million_bucks - self.one_million_bucks
        assert zeroed_test == Money(amount=0, currency=self.USD)

    def test_sub_non_money(self):
        with pytest.raises(TypeError):
            Money(1000) - 123

    def test_rsub_non_money(self):
        assert 0 - Money(1, currency=self.USD) == Money(-1, currency=self.USD)
        with pytest.raises(TypeError):
            assert 1 - Money(3, currency=self.USD) == Money(-2, currency=self.USD)

    def test_mul(self):
        x = Money(amount=111.33, currency=self.USD)
        assert 3 * x == Money(333.99, currency=self.USD)
        assert Money(333.99, currency=self.USD) == 3 * x

    def test_mul_float_warning(self):
        # This should be changed to TypeError exception after deprecation period is over.
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            Money("10", currency="ZMW") * 1.2
            assert "Multiplying Money instances with floats is deprecated" in [
                w.message.args[0] for w in warning_list
            ]

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            1.2 * Money(amount="10", currency="XAG")
            assert "Multiplying Money instances with floats is deprecated" in [
                w.message.args[0] for w in warning_list
            ]

    def test_mul_bad(self):
        with pytest.raises(TypeError):
            self.one_million_bucks * self.one_million_bucks

    def test_div(self):
        x = Money(amount=50, currency=self.USD)
        y = Money(amount=2, currency=self.USD)
        assert x / y == Decimal(25)

    def test_div_mismatched_currencies(self):
        x = Money(amount=50, currency=self.USD)
        y = Money(amount=2, currency=CURRENCIES["CAD"])
        with pytest.raises(TypeError):
            assert x / y == Money(amount=25, currency=self.USD)

    def test_div_by_non_Money(self):
        x = Money(amount=50, currency=self.USD)
        y = 2
        assert x / y == Money(amount=25, currency=self.USD)

    def test_rdiv_by_non_Money(self):
        x = 2
        y = Money(amount=50, currency=self.USD)
        with pytest.raises(TypeError):
            assert x / y == Money(amount=25, currency=self.USD)

    def test_div_float_warning(self):
        # This should be changed to TypeError exception after deprecation period is over.
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            Money(amount="10", currency=USD) / 1.2
            assert "Dividing Money instances by floats is deprecated" in [
                w.message.args[0] for w in warning_list
            ]

    def test_rmod(self):
        assert 1 % self.one_million_bucks == Money(amount=10000, currency=self.USD)

    def test_rmod_bad(self):
        with pytest.raises(TypeError):
            assert self.one_million_bucks % self.one_million_bucks == 1

    def test_rmod_float_warning(self):
        # This should be changed to TypeError exception after deprecation period is over.
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            2.0 % Money("10", USD)
            assert (
                "Calculating percentages of Money instances using floats is deprecated"
                in [w.message.args[0] for w in warning_list]
            )

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
        x = Money(amount=0, currency=self.USD)
        assert x != None  # NOQA
        assert x != {}

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

    def test_abs(self):
        abs_money = Money(amount=1, currency=self.USD)
        x = Money(amount=-1, currency=self.USD)
        assert abs(x) == abs_money
        y = Money(amount=1, currency=self.USD)
        assert abs(y) == abs_money

    def test_sum(self):
        assert sum(
            [Money(amount=1, currency=self.USD), Money(amount=2, currency=self.USD)]
        ) == Money(amount=3, currency=self.USD)

    def test_round(self):
        x = Money(amount="1234.33569", currency=self.USD)
        assert x.round(-4) == Money(amount="0", currency=self.USD)
        assert x.round(-3) == Money(amount="1000", currency=self.USD)
        assert x.round(-2) == Money(amount="1200", currency=self.USD)
        assert x.round(-1) == Money(amount="1230", currency=self.USD)
        assert x.round(0) == Money(amount="1234", currency=self.USD)
        assert x.round(None) == Money(amount="1234", currency=self.USD)
        assert x.round(1) == Money(amount="1234.3", currency=self.USD)
        assert x.round(2) == Money(amount="1234.34", currency=self.USD)
        assert x.round(3) == Money(amount="1234.336", currency=self.USD)
        assert x.round(4) == Money(amount="1234.3357", currency=self.USD)

    def test_round_context_override(self):
        import decimal

        x = Money(amount="2.5", currency=self.USD)
        assert x.round(0) == Money(amount=2, currency=self.USD)
        x = Money(amount="3.5", currency=self.USD)
        assert x.round(0) == Money(amount=4, currency=self.USD)

        with decimal.localcontext() as ctx:
            ctx.rounding = decimal.ROUND_HALF_UP
            x = Money(amount="2.5", currency=self.USD)
            assert x.round(0) == Money(amount=3, currency=self.USD)
            x = Money(amount="3.5", currency=self.USD)
            assert x.round(0) == Money(amount=4, currency=self.USD)

    def test_get_sub_unit(self):
        m = Money(amount=123, currency=self.USD)
        assert m.get_amount_in_sub_unit() == 12300

    def test_arithmetic_operations_return_real_subclass_instance(self):
        """
        Arithmetic operations on a subclass instance should return instances in the same subclass
        type.
        """

        extended_money = ExtendedMoney(amount=2, currency=self.USD)

        operated_money = +extended_money
        assert type(extended_money) == type(operated_money)
        operated_money = -extended_money
        assert type(extended_money) == type(operated_money)
        operated_money = ExtendedMoney(amount=1, currency=self.USD) + ExtendedMoney(
            amount=1, currency=self.USD
        )
        assert type(extended_money) == type(operated_money)
        operated_money = ExtendedMoney(amount=3, currency=self.USD) - Money(
            amount=1, currency=self.USD
        )
        assert type(extended_money) == type(operated_money)
        operated_money = 1 * extended_money
        assert type(extended_money) == type(operated_money)
        operated_money = extended_money / 1
        assert type(extended_money) == type(operated_money)
        operated_money = abs(ExtendedMoney(amount=-2, currency=self.USD))
        assert type(extended_money) == type(operated_money)
        operated_money = 50 % ExtendedMoney(amount=4, currency=self.USD)
        assert type(extended_money) == type(operated_money)

    def test_can_call_subclass_method_after_arithmetic_operations(self):
        """
        Calls to `ExtendedMoney::do_my_behaviour` method throws
        AttributeError: 'Money' object has no attribute 'do_my_behaviour'
        if multiplication operator doesn't return subclass instance.
        """

        extended_money = ExtendedMoney(amount=2, currency=self.USD)
        # no problem
        extended_money.do_my_behaviour()
        # throws error if `__mul__` doesn't return subclass instance
        (1 * extended_money).do_my_behaviour()

    def test_bool(self):
        assert bool(Money(amount=1, currency=self.USD))
        assert not bool(Money(amount=0, currency=self.USD))

    def test_force_decimal(self):
        assert force_decimal("53.55") == Decimal("53.55")
        assert force_decimal(53) == Decimal("53")
        assert force_decimal(Decimal("53.55")) == Decimal("53.55")

    def test_decimal_doesnt_use_str_when_multiplying(self):
        m = Money("531", "GBP")
        a = CustomDecimal("53.313")
        result = m * a
        assert result == Money("28309.203", "GBP")

    def test_decimal_doesnt_use_str_when_dividing(self):
        m = Money("15.60", "GBP")
        a = CustomDecimal("3.2")
        result = m / a
        assert result == Money("4.875", "GBP")


class ExtendedMoney(Money):
    def do_my_behaviour(self):
        pass


def test_all_babel_currencies():
    missing = sorted(set(get_global("all_currencies").keys()) - set(CURRENCIES.keys()))
    assert (
        missing == []
    ), "The following currencies defined in Babel are missing: " + ", ".join(missing)


def test_list_all_currencies():
    all_currencies = list_all_currencies()
    assert len(all_currencies) > 100
    assert [c.code for c in all_currencies[:3]] == ["ADP", "AED", "AFA"]
    assert all(isinstance(c, Currency) for c in all_currencies)
