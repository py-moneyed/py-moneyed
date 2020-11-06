# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import sys
import warnings
from decimal import Decimal

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

    def __init__(self, code='', numeric='999', name=None, countries=None):
        if countries is None:
            countries = []
        self.code = code
        self.countries = countries
        if name is not None:
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
        return "<Money: %s %s>" % (self.amount, self.currency)

    def __unicode__(self):
        from moneyed.l10n import format_money
        return format_money(self)

    if PYTHON2:
        def __str__(self):
            # On Python 2, `__str__` returns byte strings, so we can't include unicode symbols.
            # Use a simpler fallback that avoids format_money
            return '{0}{1:,}'.format(self.currency.code, self.amount)

    else:
        def __str__(self):
            from moneyed.l10n import format_money
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
            raise TypeError('Cannot add or subtract a ' +
                            'Money and non-Money instance.')
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


# ____________________________________________________________________
# Definitions of ISO 4217 Currencies
# Source: http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm  # noqa

CURRENCIES = {}
CURRENCIES_BY_ISO = {}


def add_currency(code, numeric, name, countries):
    global CURRENCIES
    CURRENCIES[code] = Currency(
        code=code,
        numeric=numeric,
        name=name,
        countries=countries)
    CURRENCIES_BY_ISO[numeric] = CURRENCIES[code]
    return CURRENCIES[code]


def get_currency(code=None, iso=None):
    try:
        if iso:
            return CURRENCIES_BY_ISO[str(iso)]
        return CURRENCIES[code]
    except KeyError:
        raise CurrencyDoesNotExist(code)


DEFAULT_CURRENCY = add_currency(DEFAULT_CURRENCY_CODE, '999', 'Default currency.', [])


AED = add_currency('AED', '784', None, ['UNITED ARAB EMIRATES'])
AFN = add_currency('AFN', '971', None, ['AFGHANISTAN'])
ALL = add_currency('ALL', '008', None, ['ALBANIA'])
AMD = add_currency('AMD', '051', None, ['ARMENIA'])
ANG = add_currency('ANG', '532', None, ['NETHERLANDS ANTILLES'])
AOA = add_currency('AOA', '973', None, ['ANGOLA'])
ARS = add_currency('ARS', '032', None, ['ARGENTINA'])
AUD = add_currency('AUD', '036', None, ['AUSTRALIA', 'CHRISTMAS ISLAND',
                                        'COCOS (KEELING) ISLANDS',
                                        'HEARD ISLAND AND MCDONALD ISLANDS',
                                        'KIRIBATI', 'NAURU', 'NORFOLK ISLAND',
                                        'TUVALU'])
AWG = add_currency('AWG', '533', None, ['ARUBA'])
AZN = add_currency('AZN', '944', None, ['AZERBAIJAN'])
BAM = add_currency('BAM', '977', None, ['BOSNIA AND HERZEGOVINA'])
BBD = add_currency('BBD', '052', None, ['BARBADOS'])
BDT = add_currency('BDT', '050', None, ['BANGLADESH'])
BGN = add_currency('BGN', '975', None, ['BULGARIA'])
BHD = add_currency('BHD', '048', None, ['BAHRAIN'])
BIF = add_currency('BIF', '108', None, ['BURUNDI'])
BMD = add_currency('BMD', '060', None, ['BERMUDA'])
BND = add_currency('BND', '096', None, ['BRUNEI DARUSSALAM'])
BOB = add_currency('BOB', '068', None, ['BOLIVIA (PLURINATIONAL STATE OF)'])
BOV = add_currency('BOV', '984', None, ['BOLIVIA (PLURINATIONAL STATE OF)'])
BRL = add_currency('BRL', '986', None, ['BRAZIL'])
BSD = add_currency('BSD', '044', None, ['BAHAMAS'])
BTN = add_currency('BTN', '064', None, ['BHUTAN'])
BWP = add_currency('BWP', '072', None, ['BOTSWANA'])
BYN = add_currency('BYN', '933', None, ['BELARUS'])
BYR = add_currency('BYR', '974', None, ['BELARUS'])
BZD = add_currency('BZD', '084', None, ['BELIZE'])
CAD = add_currency('CAD', '124', None, ['CANADA'])
CDF = add_currency('CDF', '976', None, ['DEMOCRATIC REPUBLIC OF CONGO'])
CHE = add_currency('CHE', '947', None, ['SWITZERLAND'])
CHF = add_currency('CHF', '756', None, ['LIECHTENSTEIN'])
CHW = add_currency('CHW', '948', None, ['SWITZERLAND'])
CLF = add_currency('CLF', '990', None, ['CHILE'])
CLP = add_currency('CLP', '152', None, ['CHILE'])
CNY = add_currency('CNY', '156', None, ['CHINA'])
COP = add_currency('COP', '170', None, ['COLOMBIA'])
COU = add_currency('COU', '970', None, ['COLOMBIA'])
CRC = add_currency('CRC', '188', None, ['COSTA RICA'])
CUC = add_currency('CUC', '931', None, ['CUBA'])
CUP = add_currency('CUP', '192', None, ['CUBA'])
CVE = add_currency('CVE', '132', None, ['CAPE VERDE'])
CZK = add_currency('CZK', '203', None, ['CZECH REPUBLIC'])
DJF = add_currency('DJF', '262', None, ['DJIBOUTI'])
DKK = add_currency('DKK', '208', None, ['DENMARK', 'FAROE ISLANDS', 'GREENLAND'])
DOP = add_currency('DOP', '214', None, ['DOMINICAN REPUBLIC'])
DZD = add_currency('DZD', '012', None, ['ALGERIA'])
EGP = add_currency('EGP', '818', None, ['EGYPT'])
ERN = add_currency('ERN', '232', None, ['ERITREA'])
ETB = add_currency('ETB', '230', None, ['ETHIOPIA'])
EUR = add_currency('EUR', '978', None, ['AKROTIRI AND DHEKELIA', 'ANDORRA', 'AUSTRIA', 'BELGIUM',
                                        'CYPRUS', 'ESTONIA', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE',
                                        'GUADELOUPE', 'IRELAND', 'ITALY', 'KOSOVO', 'LATVIA', 'LITHUANIA',
                                        'LUXEMBOURG', 'MALTA', 'MARTINIQUE', 'MAYOTTE', 'MONACO',
                                        'MONTENEGRO', 'NETHERLANDS', 'PORTUGAL', 'RÉUNION', 'SAINT BARTHÉLEMY',
                                        'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SLOVAKIA', 'SLOVENIA', 'SPAIN',
                                        'VATICAN CITY'])
FJD = add_currency('FJD', '242', None, ['FIJI'])
FKP = add_currency('FKP', '238', None, ['FALKLAND ISLANDS (MALVINAS)'])
GBP = add_currency('GBP', '826', None, ['UNITED KINGDOM'])
GEL = add_currency('GEL', '981', None, ['GEORGIA'])
GHS = add_currency('GHS', '936', None, ['GHANA'])
GIP = add_currency('GIP', '292', None, ['GIBRALTAR'])
GMD = add_currency('GMD', '270', None, ['GAMBIA'])
GNF = add_currency('GNF', '324', None, ['GUINEA'])
GTQ = add_currency('GTQ', '320', None, ['GUATEMALA'])
GYD = add_currency('GYD', '328', None, ['GUYANA'])
HKD = add_currency('HKD', '344', None, ['HONG KONG'])
HNL = add_currency('HNL', '340', None, ['HONDURAS'])
HRK = add_currency('HRK', '191', None, ['CROATIA'])
HTG = add_currency('HTG', '332', None, ['HAITI'])
HUF = add_currency('HUF', '348', None, ['HUNGARY'])
IDR = add_currency('IDR', '360', None, ['INDONESIA'])
ILS = add_currency('ILS', '376', None, ['ISRAEL'])
IMP = add_currency('IMP', 'Nil', None, ['ISLE OF MAN'])
INR = add_currency('INR', '356', None, ['INDIA'])
IQD = add_currency('IQD', '368', None, ['IRAQ'])
IRR = add_currency('IRR', '364', None, ['IRAN'])
ISK = add_currency('ISK', '352', None, ['ICELAND'])
JMD = add_currency('JMD', '388', None, ['JAMAICA'])
JOD = add_currency('JOD', '400', None, ['JORDAN'])
JPY = add_currency('JPY', '392', None, ['JAPAN'])
KES = add_currency('KES', '404', None, ['KENYA'])
KGS = add_currency('KGS', '417', None, ['KYRGYZSTAN'])
KHR = add_currency('KHR', '116', None, ['CAMBODIA'])
KMF = add_currency('KMF', '174', None, ['COMOROS'])
KPW = add_currency('KPW', '408', None, ['KOREA'])
KRW = add_currency('KRW', '410', None, ['KOREA'])
KWD = add_currency('KWD', '414', None, ['KUWAIT'])
KYD = add_currency('KYD', '136', None, ['CAYMAN ISLANDS'])
KZT = add_currency('KZT', '398', None, ['KAZAKHSTAN'])
LAK = add_currency('LAK', '418', None, ['LAO PEOPLES DEMOCRATIC REPUBLIC'])
LBP = add_currency('LBP', '422', None, ['LEBANON'])
LKR = add_currency('LKR', '144', None, ['SRI LANKA'])
LRD = add_currency('LRD', '430', None, ['LIBERIA'])
LSL = add_currency('LSL', '426', None, ['LESOTHO'])
LTL = add_currency('LTL', '440', None, ['LITHUANIA'])
LVL = add_currency('LVL', '428', None, ['LATVIA'])
LYD = add_currency('LYD', '434', None, ['LIBYAN ARAB JAMAHIRIYA'])
MAD = add_currency('MAD', '504', None, ['MOROCCO', 'WESTERN SAHARA'])
MDL = add_currency('MDL', '498', None, ['MOLDOVA'])
MGA = add_currency('MGA', '969', None, ['MADAGASCAR'])
MKD = add_currency('MKD', '807', None, ['MACEDONIA'])
MMK = add_currency('MMK', '104', None, ['MYANMAR'])
MNT = add_currency('MNT', '496', None, ['MONGOLIA'])
MOP = add_currency('MOP', '446', None, ['MACAO'])
MRO = add_currency('MRO', '478', None, ['MAURITANIA'])
MUR = add_currency('MUR', '480', None, ['MAURITIUS'])
MVR = add_currency('MVR', '462', None, ['MALDIVES'])
MWK = add_currency('MWK', '454', None, ['MALAWI'])
MXN = add_currency('MXN', '484', None, ['MEXICO'])
MXV = add_currency('MXV', '979', None, ['MEXICO'])
MYR = add_currency('MYR', '458', None, ['MALAYSIA'])
MZN = add_currency('MZN', '943', None, ['MOZAMBIQUE'])
NAD = add_currency('NAD', '516', None, ['NAMIBIA'])
NGN = add_currency('NGN', '566', None, ['NIGERIA'])
NIO = add_currency('NIO', '558', None, ['NICARAGUA'])
NOK = add_currency('NOK', '578', None, ['BOUVET ISLAND', 'NORWAY', 'SVALBARD AND JAN MAYEN'])
NPR = add_currency('NPR', '524', None, ['NEPAL'])
NZD = add_currency('NZD', '554', None, ['COOK ISLANDS', 'NEW ZEALAND', 'NIUE', 'PITCAIRN', 'TOKELAU'])
OMR = add_currency('OMR', '512', None, ['OMAN'])
PAB = add_currency('PAB', '590', None, ['PANAMA'])
PEN = add_currency('PEN', '604', None, ['PERU'])
PGK = add_currency('PGK', '598', None, ['PAPUA NEW GUINEA'])
PHP = add_currency('PHP', '608', None, ['PHILIPPINES'])
PKR = add_currency('PKR', '586', None, ['PAKISTAN'])
PLN = add_currency('PLN', '985', None, ['POLAND'])
PYG = add_currency('PYG', '600', None, ['PARAGUAY'])
QAR = add_currency('QAR', '634', None, ['QATAR'])
RON = add_currency('RON', '946', None, ['ROMANIA'])
RSD = add_currency('RSD', '941', None, ['SERBIA'])
RUB = add_currency('RUB', '643', None, ['RUSSIAN FEDERATION'])
RWF = add_currency('RWF', '646', None, ['RWANDA'])
SAR = add_currency('SAR', '682', None, ['SAUDI ARABIA'])
SBD = add_currency('SBD', '090', None, ['SOLOMON ISLANDS'])
SCR = add_currency('SCR', '690', None, ['SEYCHELLES'])
SDG = add_currency('SDG', '938', None, ['SUDAN'])
SEK = add_currency('SEK', '752', None, ['SWEDEN'])
SGD = add_currency('SGD', '702', None, ['SINGAPORE'])
SHP = add_currency('SHP', '654', None, ['SAINT HELENA'])
SLL = add_currency('SLL', '694', None, ['SIERRA LEONE'])
SOS = add_currency('SOS', '706', None, ['SOMALIA'])
SRD = add_currency('SRD', '968', None, ['SURINAME'])
SSP = add_currency('SSP', '728', None, ['SOUTH SUDAN'])
STD = add_currency('STD', '678', None, ['SAO TOME AND PRINCIPE'])
SVC = add_currency('SVC', '222', None, ['EL SALVADOR'])
SYP = add_currency('SYP', '760', None, ['SYRIAN ARAB REPUBLIC'])
SZL = add_currency('SZL', '748', None, ['SWAZILAND'])
THB = add_currency('THB', '764', None, ['THAILAND'])
TJS = add_currency('TJS', '972', None, ['TAJIKISTAN'])
TMM = add_currency('TMM', '795', None, ['TURKMENISTAN'])
TMT = add_currency('TMT', '934', None, ['TURKMENISTAN'])
TND = add_currency('TND', '788', None, ['TUNISIA'])
TOP = add_currency('TOP', '776', None, ['TONGA'])
TRY = add_currency('TRY', '949', None, ['TURKEY'])
TTD = add_currency('TTD', '780', None, ['TRINIDAD AND TOBAGO'])
TVD = add_currency('TVD', 'Nil', None, ['TUVALU'])
TWD = add_currency('TWD', '901', None, ['TAIWAN'])
TZS = add_currency('TZS', '834', None, ['TANZANIA'])
UAH = add_currency('UAH', '980', None, ['UKRAINE'])
UGX = add_currency('UGX', '800', None, ['UGANDA'])
USD = add_currency('USD', '840', None, ['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY',
                                        'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA',
                                        'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO',
                                        'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES',
                                        'UNITED STATES MINOR OUTLYING ISLANDS',
                                        'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
USN = add_currency('USN', '997', None, ['UNITED STATES OF AMERICA (THE)'])
UYI = add_currency('UYI', '940', None, ['URUGUAY'])
UYU = add_currency('UYU', '858', None, ['URUGUAY'])
UZS = add_currency('UZS', '860', None, ['UZBEKISTAN'])
VEF = add_currency('VEF', '937', None, ['VENEZUELA'])
VND = add_currency('VND', '704', None, ['VIET NAM'])
VUV = add_currency('VUV', '548', None, ['VANUATU'])
WST = add_currency('WST', '882', None, ['SAMOA'])
XAF = add_currency('XAF', '950', None, ['CAMEROON', 'CENTRAL AFRICAN REPUBLIC',
                                        'REPUBLIC OF THE CONGO', 'CHAD', 'EQUATORIAL GUINEA',
                                        'GABON'])
XAG = add_currency('XAG', '961', None, [])
XAU = add_currency('XAU', '959', None, [])
XBA = add_currency('XBA', '955', None, [])
XBB = add_currency('XBB', '956', None, [])
XBC = add_currency('XBC', '957', None, [])
XBD = add_currency('XBD', '958', None, [])
XCD = add_currency('XCD', '951', None, ['ANGUILLA', 'ANTIGUA AND BARBUDA', 'DOMINICA',
                                        'GRENADA', 'MONTSERRAT', 'SAINT KITTS AND NEVIS',
                                        'SAINT LUCIA', 'SAINT VINCENT AND THE GRENADINES'])
XDR = add_currency('XDR', '960', None, ['INTERNATIONAL MONETARY FUND (I.M.F)'])
XFO = add_currency('XFO', 'Nil', None, [])
XFU = add_currency('XFU', 'Nil', None, [])
XOF = add_currency('XOF', '952', None, ['BENIN', 'BURKINA FASO', 'COTE D\'IVOIRE',
                                        'GUINEA-BISSAU', 'MALI', 'NIGER', 'SENEGAL', 'TOGO'])
XPD = add_currency('XPD', '964', None, [])
XPF = add_currency('XPF', '953', None, ['FRENCH POLYNESIA', 'NEW CALEDONIA', 'WALLIS AND FUTUNA'])
XPT = add_currency('XPT', '962', None, [])
XSU = add_currency('XSU', '994', None, ['SISTEMA UNITARIO DE COMPENSACION REGIONAL DE PAGOS "SUCRE"'])
XTS = add_currency('XTS', '963', None, [])
XUA = add_currency('XUA', '965', None, ['MEMBER COUNTRIES OF THE AFRICAN DEVELOPMENT BANK GROUP'])
XXX = add_currency(
    'XXX',
    '999',
    'The codes assigned for transactions where no currency is involved',
    ['ZZ07_No_Currency'],
)
YER = add_currency('YER', '886', None, ['YEMEN'])
ZAR = add_currency('ZAR', '710', None, ['SOUTH AFRICA'])
ZMK = add_currency('ZMK', '894', None, [])  # historical
ZMW = add_currency('ZMW', '967', None, ['ZAMBIA'])
ZWD = add_currency('ZWD', '716', None, ['ZIMBABWE'])
ZWL = add_currency('ZWL', '932', None, ['ZIMBABWE'])
ZWN = add_currency('ZWN', '942', None, ['ZIMBABWE'])
