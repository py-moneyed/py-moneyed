# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import sys
import warnings
from decimal import Decimal

from babel import Locale
from babel.core import get_global

from .l10n import format_money
from .utils import cached_property

# Default, non-existent, currency
DEFAULT_CURRENCY_CODE = 'XYZ'

PYTHON2 = sys.version_info[0] == 2


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

    def __init__(self, code='', numeric=None, sub_unit=1, name=None, countries=None):
        self.code = code
        self.numeric = numeric
        self.sub_unit = sub_unit
        if name is not None:
            self.name = name
        if countries is not None:
            self.countries = countries

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        return type(self) is type(other) and self.code == other.code

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.code

    def __lt__(self, other):
        return self.code < other.code

    def __le__(self, other):
        return self.code <= other.code

    @cached_property
    def name(self):
        """"
        Name of the currency in US locale. For backwards compat.

        Consider using get_name() instead, or babel.numbers.get_currency_name()
        """
        return self.get_name('en_US')

    def get_name(self, locale, count=None):
        from babel.numbers import get_currency_name
        return get_currency_name(self.code, locale=locale, count=count)

    @cached_property
    def countries(self):
        """
        List of country names, uppercased and in US locale, where the currency is
        used at present.

        DEPRECATED. Use `.country_codes` instead, and get_country_name() to
        convert these to a country name in your desired locale.

        """
        return [get_country_name(country_code, 'en_US').upper()
                for country_code in self.country_codes]

    @cached_property
    def country_codes(self):
        """
        List of current country codes for the currency.
        """
        return [
            territory.upper()
            for territory, currencies in get_global('territory_currencies').items()
            for currency_code, start, end, is_tender in currencies
            if end is None and currency_code == self.code
        ]


def get_country_name(country_code, locale):
    return Locale.parse(locale).territories[country_code]


class MoneyComparisonError(TypeError):
    # This exception was needed often enough to merit its own
    # Exception class.

    def __init__(self, other):
        assert not isinstance(other, Money)
        self.other = other

    def __str__(self):
        # Note: at least w/ Python 2.x, use __str__, not __unicode__.
        return "Cannot compare instances of Money and %s" \
               % self.other.__class__.__name__


class CurrencyDoesNotExist(Exception):

    def __init__(self, code):
        super(CurrencyDoesNotExist, self).__init__(
            "No currency with code %s is defined." % code)


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
        return "Money('%s', '%s')" % (self.amount, self.currency)

    def __unicode__(self):
        return format_money(self)

    if PYTHON2:
        def __str__(self):
            # On Python 2, `__str__` returns byte strings, so we can't include unicode symbols.
            # Use a simpler fallback that avoids format_money
            return '{0}{1:,}'.format(self.currency.code, self.amount)

    else:
        def __str__(self):
            return format_money(self)

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __pos__(self):
        return self.__class__(
            amount=self.amount,
            currency=self.currency)

    def __neg__(self):
        return self.__class__(
            amount=-self.amount,
            currency=self.currency)

    def __add__(self, other):
        if other == 0:
            # This allows things like 'sum' to work on list of Money instances,
            # just like list of Decimal.
            return self
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency == other.currency:
            return self.__class__(
                amount=self.amount + other.amount,
                currency=self.currency)

        raise TypeError('Cannot add or subtract two Money ' +
                        'instances with different currencies.')

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        if isinstance(other, Money):
            raise TypeError('Cannot multiply two Money instances.')
        else:
            if isinstance(other, float):
                warnings.warn("Multiplying Money instances with floats is deprecated", DeprecationWarning)
            return self.__class__(
                amount=(self.amount * force_decimal(other)),
                currency=self.currency)

    def __truediv__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise TypeError('Cannot divide two different currencies.')
            return self.amount / other.amount
        else:
            if isinstance(other, float):
                warnings.warn("Dividing Money instances by floats is deprecated", DeprecationWarning)
            return self.__class__(
                amount=(self.amount / force_decimal(other)),
                currency=self.currency)

    def __rtruediv__(self, other):
        raise TypeError('Cannot divide non-Money by a Money instance.')

    def round(self, ndigits=0):
        """
        Rounds the amount using the current ``Decimal`` rounding algorithm.
        """
        if ndigits is None:
            ndigits = 0
        return self.__class__(
            amount=self.amount.quantize(Decimal('1e' + str(-ndigits))),
            currency=self.currency)

    def __abs__(self):
        return self.__class__(
            amount=abs(self.amount),
            currency=self.currency)

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
                warnings.warn("Calculating percentages of Money instances using floats is deprecated",
                              DeprecationWarning)
            return self.__class__(
                amount=(Decimal(str(other)) * self.amount / 100),
                currency=self.currency)

    __radd__ = __add__
    __rmul__ = __mul__

    # _______________________________________
    # Override comparison operators
    def __eq__(self, other):
        return (isinstance(other, Money) and
                (self.amount == other.amount) and
                (self.currency == other.currency))

    def __ne__(self, other):
        result = self.__eq__(other)
        return not result

    def __lt__(self, other):
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if (self.currency == other.currency):
            return (self.amount < other.amount)
        else:
            raise TypeError('Cannot compare Money with different currencies.')

    def __gt__(self, other):
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if (self.currency == other.currency):
            return (self.amount > other.amount)
        else:
            raise TypeError('Cannot compare Money with different currencies.')

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def get_amount_in_sub_unit(self):
        return int(self.currency.sub_unit * self.amount)


# ____________________________________________________________________
# Definitions of ISO 4217 Currencies
# Source: http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm  # noqa

CURRENCIES = {}
CURRENCIES_BY_ISO = {}


def add_currency(code, numeric, sub_unit=1, name=None, countries=None):
    currency = Currency(code=code, numeric=numeric, sub_unit=sub_unit, name=name, countries=countries)
    CURRENCIES[code] = currency
    # No lookup by numeric code for currencies without numeric codes
    if numeric is not None:
        CURRENCIES_BY_ISO[numeric] = currency
    return currency


def get_currency(code=None, iso=None):
    try:
        if iso:
            return CURRENCIES_BY_ISO[str(iso)]
        return CURRENCIES[code]
    except KeyError:
        raise CurrencyDoesNotExist(code)


def get_currencies_of_country(country_code):
    """
    Returns list with currency object(s) given the country's ISO-2 code.
    Raises a CountryDoesNotExist exception if the country is not found.

    country : str
    The full name of the country to be searched for.
    """
    country_code = country_code.upper()
    return sorted([
        currency
        for currency in CURRENCIES.values()
        if country_code in currency.country_codes
    ])


def list_all_currencies():
    return sorted(CURRENCIES.values(), key=lambda c: c.code)


DEFAULT_CURRENCY = add_currency(DEFAULT_CURRENCY_CODE, None, 1, 'Default currency.', [])

# The order of registration is important because we want active currencies to be available via `get_currency`.
# For this reason, we have obsolete currencies first, and then they may be overridden by active ones
# Obsolete currencies
ADP = add_currency('ADP', '020')
AFA = add_currency('AFA', '004', 100)
ALK = add_currency('ALK', '008')
AON = add_currency('AON', '024')
AOR = add_currency('AOR', '982')
ARA = add_currency('ARA', '032', 100)
ARP = add_currency('ARP', '032', 100)
ATS = add_currency('ATS', '040', 100)
AZM = add_currency('AZM', '031', 100)
BAD = add_currency('BAD', '070', 100)
BEF = add_currency('BEF', '056', 100)
BGL = add_currency('BGL', '100', 100)
BRC = add_currency('BRC', '076', 100)
BRE = add_currency('BRE', '076', 100)
BRN = add_currency('BRN', '076', 100)
BRR = add_currency('BRR', '987', 100)
BYR = add_currency('BYR', '974')
CLE = add_currency('CLE', '152')
CSD = add_currency('CSD', '891', 100)
CSK = add_currency('CSK', '200')
CYP = add_currency('CYP', '196', 100)
DDM = add_currency('DDM', '278')
DEM = add_currency('DEM', '276', 100)
ECS = add_currency('ECS', '218')
ECV = add_currency('ECV', '983', 100)
EEK = add_currency('EEK', '233', 100)
ESA = add_currency('ESA', '996')
ESB = add_currency('ESB', '995')
ESP = add_currency('ESP', '020')
FIM = add_currency('FIM', '246', 100)
FRF = add_currency('FRF', '250', 100)
GHC = add_currency('GHC', '288', 100)
GRD = add_currency('GRD', '300', 100)
GWP = add_currency('GWP', '624', 100)
HRD = add_currency('HRD', '191', 100)
IEP = add_currency('IEP', '372', 100)
ITL = add_currency('ITL', '380')
LTL = add_currency('LTL', '440', 100)
LUF = add_currency('LUF', '442', 100)
LVL = add_currency('LVL', '428', 100)
MGF = add_currency('MGF', '450')
MLF = add_currency('MLF', '466')
MRO = add_currency('MRO', '478', 100)
MTL = add_currency('MTL', '470', 100)
MZM = add_currency('MZM', '508', 100)
NLG = add_currency('NLG', '528', 100)
PEI = add_currency('PEI', '604')
PLZ = add_currency('PLZ', '616', 100)
PTE = add_currency('PTE', '620')
ROL = add_currency('ROL', '642')
RUR = add_currency('RUR', '810', 100)
SDD = add_currency('SDD', '736', 100)
SIT = add_currency('SIT', '705', 100)
SKK = add_currency('SKK', '703', 100)
SRG = add_currency('SRG', '740', 100)
STD = add_currency('STD', '678', 100)
TJR = add_currency('TJR', '762')
TMM = add_currency('TMM', '795', 100)
TPE = add_currency('TPE', '626')
TRL = add_currency('TRL', '792')
UAK = add_currency('UAK', '804', 100)
USS = add_currency('USS', '998', 100)
VEB = add_currency('VEB', '862', 100)
VEF = add_currency('VEF', '937', 100)
VNN = add_currency('VNN', '704')
XEU = add_currency('XEU', '954')
YDD = add_currency('YDD', '710')
YUM = add_currency('YUM', '891', 100)
YUN = add_currency('YUN', '890', 100)
ZAL = add_currency('ZAL', '991', 100)
ZMK = add_currency('ZMK', '894', 100)
ZRN = add_currency('ZRN', '180', 100)
ZRZ = add_currency('ZRZ', '180', 100)
ZWD = add_currency('ZWD', '716', 100)
ZWL = add_currency('ZWL', '932', 100)
ZWR = add_currency('ZWR', '935', 100)

# Further obsolete currencies that don't appear to have ISO 4217 codes
AOK = add_currency('AOK', None)
ARL = add_currency('ARL', None, 100)
ARM = add_currency('ARM', None, 100)
BAN = add_currency('BAN', None)
BEC = add_currency('BEC', None)
BEL = add_currency('BEL', None)
BGM = add_currency('BGM', None)
BGO = add_currency('BGO', None)
BOL = add_currency('BOL', None)
BOP = add_currency('BOP', None, 100)
BRB = add_currency('BRB', None, 100)
BRZ = add_currency('BRZ', None, 100)
BUK = add_currency('BUK', None)
BYB = add_currency('BYB', None, 100)
CNH = add_currency('CNH', None, 100)
CNX = add_currency('CNX', None, 100)
GEK = add_currency('GEK', None)
GNS = add_currency('GNS', None)
GQE = add_currency('GQE', None)
GWE = add_currency('GWE', None)
ILP = add_currency('ILP', None, 100)
ILR = add_currency('ILR', None, 100)
ISJ = add_currency('ISJ', None, 100)
KRH = add_currency('KRH', None)
KRO = add_currency('KRO', None)
LTT = add_currency('LTT', None, 100)
LUC = add_currency('LUC', None)
LUL = add_currency('LUL', None)
LVR = add_currency('LVR', None, 100)
MAF = add_currency('MAF', None, 100)
MCF = add_currency('MCF', None, 100)
MDC = add_currency('MDC', None)
MKN = add_currency('MKN', None)
MRU = add_currency('MRU', None, 100)
MTP = add_currency('MTP', None)
MVP = add_currency('MVP', None)
MXP = add_currency('MXP', None)
MZE = add_currency('MZE', None, 100)
NIC = add_currency('NIC', None, 100)
PES = add_currency('PES', None, 100)
RHD = add_currency('RHD', None, 100)
SDP = add_currency('SDP', None)
STN = add_currency('STN', None, 100)
SUR = add_currency('SUR', None)
UGS = add_currency('UGS', None)
UYP = add_currency('UYP', None, 100)
UYW = add_currency('UYW', None, 10000)
VES = add_currency('VES', None, 100)
XRE = add_currency('XRE', None)
YUD = add_currency('YUD', None, 100)
YUR = add_currency('YUR', None, 100)


# Active currencies
AED = add_currency('AED', '784', 100)
AFN = add_currency('AFN', '971', 100)
ALL = add_currency('ALL', '008', 100)
AMD = add_currency('AMD', '051', 100)
ANG = add_currency('ANG', '532', 100)
AOA = add_currency('AOA', '973', 100)
ARS = add_currency('ARS', '032', 100)
AUD = add_currency('AUD', '036', 100)
AWG = add_currency('AWG', '533', 100)
AZN = add_currency('AZN', '944', 100)
BAM = add_currency('BAM', '977', 100)
BBD = add_currency('BBD', '052', 100)
BDT = add_currency('BDT', '050', 100)
BGN = add_currency('BGN', '975', 100)
BHD = add_currency('BHD', '048', 1000)
BIF = add_currency('BIF', '108')
BMD = add_currency('BMD', '060', 100)
BND = add_currency('BND', '096', 100)
BOB = add_currency('BOB', '068', 100)
BOV = add_currency('BOV', '984', 100)
BRL = add_currency('BRL', '986', 100)
BSD = add_currency('BSD', '044', 100)
BTN = add_currency('BTN', '064', 100)
BWP = add_currency('BWP', '072', 100)
BYN = add_currency('BYN', '933', 100)
BZD = add_currency('BZD', '084', 100)
CAD = add_currency('CAD', '124', 100)
CDF = add_currency('CDF', '976', 100)
CHE = add_currency('CHE', '947', 100)
CHF = add_currency('CHF', '756', 100)
CHW = add_currency('CHW', '948', 100)
CLF = add_currency('CLF', '990', 10000)
CLP = add_currency('CLP', '152')
CNY = add_currency('CNY', '156', 100)
COP = add_currency('COP', '170', 100)
COU = add_currency('COU', '970', 100)
CRC = add_currency('CRC', '188', 100)
CUC = add_currency('CUC', '931', 100)
CUP = add_currency('CUP', '192', 100)
CVE = add_currency('CVE', '132', 100)
CZK = add_currency('CZK', '203', 100)
DJF = add_currency('DJF', '262')
DKK = add_currency('DKK', '208', 100)
DOP = add_currency('DOP', '214', 100)
DZD = add_currency('DZD', '012', 100)
EGP = add_currency('EGP', '818', 100)
ERN = add_currency('ERN', '232', 100)
ETB = add_currency('ETB', '230', 100)
EUR = add_currency('EUR', '978', 100)
FJD = add_currency('FJD', '242', 100)
FKP = add_currency('FKP', '238', 100)
GBP = add_currency('GBP', '826', 100)
GEL = add_currency('GEL', '981', 100)
GHS = add_currency('GHS', '936', 100)
GIP = add_currency('GIP', '292', 100)
GMD = add_currency('GMD', '270', 100)
GNF = add_currency('GNF', '324')
GTQ = add_currency('GTQ', '320', 100)
GYD = add_currency('GYD', '328', 100)
HKD = add_currency('HKD', '344', 100)
HNL = add_currency('HNL', '340', 100)
HRK = add_currency('HRK', '191', 100)
HTG = add_currency('HTG', '332', 100)
HUF = add_currency('HUF', '348', 100)
IDR = add_currency('IDR', '360', 100)
ILS = add_currency('ILS', '376', 100)
IMP = add_currency('IMP', None, 100)
INR = add_currency('INR', '356', 100)
IQD = add_currency('IQD', '368', 1000)
IRR = add_currency('IRR', '364', 100)
ISK = add_currency('ISK', '352')
JMD = add_currency('JMD', '388', 100)
JOD = add_currency('JOD', '400', 1000)
JPY = add_currency('JPY', '392')
KES = add_currency('KES', '404', 100)
KGS = add_currency('KGS', '417', 100)
KHR = add_currency('KHR', '116', 100)
KMF = add_currency('KMF', '174')
KPW = add_currency('KPW', '408', 100)
KRW = add_currency('KRW', '410')
KWD = add_currency('KWD', '414', 1000)
KYD = add_currency('KYD', '136', 100)
KZT = add_currency('KZT', '398', 100)
LAK = add_currency('LAK', '418', 100)
LBP = add_currency('LBP', '422', 100)
LKR = add_currency('LKR', '144', 100)
LRD = add_currency('LRD', '430', 100)
LSL = add_currency('LSL', '426', 100)
LYD = add_currency('LYD', '434', 1000)
MAD = add_currency('MAD', '504', 100)
MDL = add_currency('MDL', '498', 100)
MGA = add_currency('MGA', '969', 100)
MKD = add_currency('MKD', '807', 100)
MMK = add_currency('MMK', '104', 100)
MNT = add_currency('MNT', '496', 100)
MOP = add_currency('MOP', '446', 100)
MUR = add_currency('MUR', '480', 100)
MVR = add_currency('MVR', '462', 100)
MWK = add_currency('MWK', '454', 100)
MXN = add_currency('MXN', '484', 100)
MXV = add_currency('MXV', '979', 100)
MYR = add_currency('MYR', '458', 100)
MZN = add_currency('MZN', '943', 100)
NAD = add_currency('NAD', '516', 100)
NGN = add_currency('NGN', '566', 100)
NIO = add_currency('NIO', '558', 100)
NOK = add_currency('NOK', '578', 100)
NPR = add_currency('NPR', '524', 100)
NZD = add_currency('NZD', '554', 100)
OMR = add_currency('OMR', '512', 1000)
PAB = add_currency('PAB', '590', 100)
PEN = add_currency('PEN', '604', 100)
PGK = add_currency('PGK', '598', 100)
PHP = add_currency('PHP', '608', 100)
PKR = add_currency('PKR', '586', 100)
PLN = add_currency('PLN', '985', 100)
PYG = add_currency('PYG', '600')
QAR = add_currency('QAR', '634', 100)
RON = add_currency('RON', '946', 100)
RSD = add_currency('RSD', '941', 100)
RUB = add_currency('RUB', '643', 100)
RWF = add_currency('RWF', '646')
SAR = add_currency('SAR', '682', 100)
SBD = add_currency('SBD', '090', 100)
SCR = add_currency('SCR', '690', 100)
SDG = add_currency('SDG', '938', 100)
SEK = add_currency('SEK', '752', 100)
SGD = add_currency('SGD', '702', 100)
SHP = add_currency('SHP', '654', 100)
SLL = add_currency('SLL', '694', 100)
SOS = add_currency('SOS', '706', 100)
SRD = add_currency('SRD', '968', 100)
SSP = add_currency('SSP', '728', 100)
SVC = add_currency('SVC', '222', 100)
SYP = add_currency('SYP', '760', 100)
SZL = add_currency('SZL', '748', 100)
THB = add_currency('THB', '764', 100)
TJS = add_currency('TJS', '972', 100)
TMT = add_currency('TMT', '934', 100)
TND = add_currency('TND', '788', 1000)
TOP = add_currency('TOP', '776', 100)
TRY = add_currency('TRY', '949', 100)
TTD = add_currency('TTD', '780', 100)
TVD = add_currency('TVD', None, 100)
TWD = add_currency('TWD', '901', 100)
TZS = add_currency('TZS', '834', 100)
UAH = add_currency('UAH', '980', 100)
UGX = add_currency('UGX', '800')
USD = add_currency('USD', '840', 100)
USN = add_currency('USN', '997', 100)
UYI = add_currency('UYI', '940')
UYU = add_currency('UYU', '858', 100)
UZS = add_currency('UZS', '860', 100)
VND = add_currency('VND', '704')
VUV = add_currency('VUV', '548')
WST = add_currency('WST', '882', 100)
XAF = add_currency('XAF', '950')
XAG = add_currency('XAG', '961')
XAU = add_currency('XAU', '959')
XBA = add_currency('XBA', '955')
XBB = add_currency('XBB', '956')
XBC = add_currency('XBC', '957')
XBD = add_currency('XBD', '958')
XCD = add_currency('XCD', '951', 100)
XDR = add_currency('XDR', '960')
XFO = add_currency('XFO', None)
XFU = add_currency('XFU', None)
XOF = add_currency('XOF', '952')
XPD = add_currency('XPD', '964')
XPF = add_currency('XPF', '953')
XPT = add_currency('XPT', '962')
XSU = add_currency('XSU', '994')
XTS = add_currency('XTS', '963')
XUA = add_currency('XUA', '965')
XXX = add_currency(
    'XXX',
    '999',
    # For backwards compat we keep values here, instead of getting
    # Babel's data.
    name='The codes assigned for transactions where no currency is involved',
    countries=['ZZ07_No_Currency'],
)
YER = add_currency('YER', '886', 100)
ZAR = add_currency('ZAR', '710', 100)
ZMW = add_currency('ZMW', '967', 100)
ZWN = add_currency('ZWN', '942', 100)
