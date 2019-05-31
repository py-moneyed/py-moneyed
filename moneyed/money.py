# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import unicode_literals

from decimal import Decimal
import sys
import warnings


PYTHON2 = sys.version_info[0] == 2

# Default, non-existent, currency
DEFAULT_CURRENCY_CODE = 'XYZ'


def force_decimal(amount):
    """Given an amount of unknown type, type cast it to be a Decimal."""
    if not isinstance(amount, Decimal):
        return Decimal(str(amount))
    return amount


class Currency(object):
    """
    A Currency represents a form of money issued by governments, and
    used in one or more states/countries.  A Currency instance
    encapsulates the related data of: the ISO currency/numeric code, a
    canonical name, and countries the currency is used in.
    """

    def __init__(self, code='', numeric='999', name='', countries=None):
        if countries is None:
            countries = []
        self.code = code
        self.countries = countries
        self.name = name
        self.numeric = numeric

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        return type(self) is type(other) and self.code == other.code

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.code


class MoneyComparisonError(TypeError):
    # This exception was needed often enough to merit its own
    # Exception class.

    def __init__(self, other):
        assert not isinstance(other, Money)
        self.other = other

    def __str__(self):
        # Note: at least w/ Python 2.x, use __str__, not __unicode__.
        return (
            "Cannot compare instances of Money and %s" % self.other.__class__.__name__
        )


class CurrencyDoesNotExist(Exception):
    def __init__(self, code):
        super(CurrencyDoesNotExist, self).__init__(
            "No currency with code %s is defined." % code
        )


class Money(object):
    """
    A Money instance is a combination of data - an amount and a
    currency - along with operators that handle the semantics of money
    operations in a better way than just dealing with raw Decimal or
    ($DEITY forbid) floats.
    """

    def __init__(self, amount=Decimal('0.0'), currency=DEFAULT_CURRENCY_CODE):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        self.amount = amount

        if not isinstance(currency, Currency):
            currency = get_currency(str(currency).upper())
        self.currency = currency

    def __repr__(self):
        return "<Money: %s %s>" % (self.amount, self.currency)

    def __unicode__(self):
        from moneyed.localization import format_money

        return format_money(self)

    def __str__(self):
        from moneyed.localization import format_money

        if PYTHON2:
            return '%s%s' % (
                self.currency.code,
                format_money(self, include_symbol=False),
            )
        else:
            return format_money(self)

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __pos__(self):
        return self.__class__(amount=self.amount, currency=self.currency)

    def __neg__(self):
        return self.__class__(amount=-self.amount, currency=self.currency)

    def __add__(self, other):
        if other == 0:
            # This allows things like 'sum' to work on list of Money instances,
            # just like list of Decimal.
            return self
        if not isinstance(other, Money):
            raise TypeError(
                'Cannot add or subtract a ' + 'Money and non-Money instance.'
            )
        if self.currency == other.currency:
            return self.__class__(
                amount=self.amount + other.amount, currency=self.currency
            )

        raise TypeError(
            'Cannot add or subtract two Money ' + 'instances with different currencies.'
        )

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        if isinstance(other, Money):
            raise TypeError('Cannot multiply two Money instances.')
        else:
            if isinstance(other, float):
                warnings.warn(
                    "Multiplying Money instances with floats is deprecated",
                    DeprecationWarning,
                )
            return self.__class__(
                amount=(self.amount * force_decimal(other)), currency=self.currency
            )

    def __truediv__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise TypeError('Cannot divide two different currencies.')
            return self.amount / other.amount
        else:
            if isinstance(other, float):
                warnings.warn(
                    "Dividing Money instances by floats is deprecated",
                    DeprecationWarning,
                )
            return self.__class__(
                amount=(self.amount / force_decimal(other)), currency=self.currency
            )

    def round(self, ndigits=0):
        """
        Rounds the amount using the current ``Decimal`` rounding algorithm.
        """
        if ndigits is None:
            ndigits = 0
        return self.__class__(
            amount=self.amount.quantize(Decimal('1e' + str(-ndigits))),
            currency=self.currency,
        )

    def __abs__(self):
        return self.__class__(amount=abs(self.amount), currency=self.currency)

    def __bool__(self):
        return bool(self.amount)

    if PYTHON2:
        __nonzero__ = __bool__

    def __rmod__(self, other):
        """
        Calculate percentage of an amount.  The left-hand side of the
        operator must be a numeric value.

        Example:
        >>> money = Money(200, 'USD')
        >>> 5 % money
        USD 10.00
        """
        if isinstance(other, Money):
            raise TypeError('Invalid __rmod__ operation')
        else:
            if isinstance(other, float):
                warnings.warn(
                    "Calculating percentages of Money instances using floats is deprecated",
                    DeprecationWarning,
                )
            return self.__class__(
                amount=(Decimal(str(other)) * self.amount / 100), currency=self.currency
            )

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rtruediv__ = __truediv__

    # _______________________________________
    # Override comparison operators
    def __eq__(self, other):
        return (
            isinstance(other, Money)
            and (self.amount == other.amount)
            and (self.currency == other.currency)
        )

    def __ne__(self, other):
        result = self.__eq__(other)
        return not result

    def __lt__(self, other):
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if self.currency == other.currency:
            return self.amount < other.amount
        else:
            raise TypeError('Cannot compare Money with different currencies.')

    def __gt__(self, other):
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if self.currency == other.currency:
            return self.amount > other.amount
        else:
            raise TypeError('Cannot compare Money with different currencies.')

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other


CURRENCIES = {}
CURRENCIES_BY_ISO = {}


def add_currency(code, numeric, name, countries):
    global CURRENCIES
    CURRENCIES[code] = Currency(
        code=code, numeric=numeric, name=name, countries=countries
    )
    CURRENCIES_BY_ISO[numeric] = CURRENCIES[code]
    return CURRENCIES[code]


def get_currency(code=None, iso=None):
    try:
        if iso:
            return CURRENCIES_BY_ISO[str(iso)]
        return CURRENCIES[code]
    except KeyError:
        raise CurrencyDoesNotExist(code)
