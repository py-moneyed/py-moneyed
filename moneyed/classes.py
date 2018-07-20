# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import unicode_literals

from decimal import Decimal
import sys
import warnings

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
        from moneyed.localization import format_money
        return format_money(self)

    def __str__(self):
        from moneyed.localization import format_money
        if PYTHON2:
            return '%s%s' % (self.currency.code, format_money(self, include_symbol=False))
        else:
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
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rtruediv__ = __truediv__

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


AED = add_currency('AED', '784', 'UAE Dirham', ['UNITED ARAB EMIRATES'])
AFN = add_currency('AFN', '971', 'Afghani', ['AFGHANISTAN'])
ALL = add_currency('ALL', '008', 'Lek', ['ALBANIA'])
AMD = add_currency('AMD', '051', 'Armenian Dram', ['ARMENIA'])
ANG = add_currency('ANG', '532', 'Netherlands Antillian Guilder', ['NETHERLANDS ANTILLES'])
AOA = add_currency('AOA', '973', 'Kwanza', ['ANGOLA'])
ARS = add_currency('ARS', '032', 'Argentine Peso', ['ARGENTINA'])
AUD = add_currency('AUD', '036', 'Australian Dollar', ['AUSTRALIA', 'CHRISTMAS ISLAND',
                                                       'COCOS (KEELING) ISLANDS',
                                                       'HEARD ISLAND AND MCDONALD ISLANDS',
                                                       'KIRIBATI', 'NAURU', 'NORFOLK ISLAND',
                                                       'TUVALU'])
AWG = add_currency('AWG', '533', 'Aruban Guilder', ['ARUBA'])
AZN = add_currency('AZN', '944', 'Azerbaijanian Manat', ['AZERBAIJAN'])
BAM = add_currency('BAM', '977', 'Convertible Marks', ['BOSNIA AND HERZEGOVINA'])
BBD = add_currency('BBD', '052', 'Barbados Dollar', ['BARBADOS'])
BDT = add_currency('BDT', '050', 'Taka', ['BANGLADESH'])
BGN = add_currency('BGN', '975', 'Bulgarian Lev', ['BULGARIA'])
BHD = add_currency('BHD', '048', 'Bahraini Dinar', ['BAHRAIN'])
BIF = add_currency('BIF', '108', 'Burundi Franc', ['BURUNDI'])
BMD = add_currency('BMD', '060', 'Bermudian Dollar (customarily known as Bermuda Dollar)', ['BERMUDA'])
BND = add_currency('BND', '096', 'Brunei Dollar', ['BRUNEI DARUSSALAM'])
BOB = add_currency('BOB', '068', 'Boliviano', ['BOLIVIA (PLURINATIONAL STATE OF)'])
BOV = add_currency('BOV', '984', 'Mvdol', ['BOLIVIA (PLURINATIONAL STATE OF)'])
BRL = add_currency('BRL', '986', 'Brazilian Real', ['BRAZIL'])
BSD = add_currency('BSD', '044', 'Bahamian Dollar', ['BAHAMAS'])
BTN = add_currency('BTN', '064', 'Bhutanese ngultrum', ['BHUTAN'])
BWP = add_currency('BWP', '072', 'Pula', ['BOTSWANA'])
BYN = add_currency('BYN', '933', 'Belarussian Ruble', ['BELARUS'])
BYR = add_currency('BYR', '974', 'Belarussian Ruble', ['BELARUS'])
BZD = add_currency('BZD', '084', 'Belize Dollar', ['BELIZE'])
CAD = add_currency('CAD', '124', 'Canadian Dollar', ['CANADA'])
CDF = add_currency('CDF', '976', 'Congolese franc', ['DEMOCRATIC REPUBLIC OF CONGO'])
CHE = add_currency('CHE', '947', 'WIR Euro', ['SWITZERLAND'])
CHF = add_currency('CHF', '756', 'Swiss Franc', ['LIECHTENSTEIN'])
CHW = add_currency('CHW', '948', 'WIR Franc', ['SWITZERLAND'])
CLF = add_currency('CLF', '990', 'Unidad de Fomento', ['CHILE'])
CLP = add_currency('CLP', '152', 'Chilean peso', ['CHILE'])
CNY = add_currency('CNY', '156', 'Yuan Renminbi', ['CHINA'])
COP = add_currency('COP', '170', 'Colombian peso', ['COLOMBIA'])
COU = add_currency('COU', '970', 'Unidad de Valor Real', ['COLOMBIA'])
CRC = add_currency('CRC', '188', 'Costa Rican Colon', ['COSTA RICA'])
CUC = add_currency('CUC', '931', 'Cuban convertible peso', ['CUBA'])
CUP = add_currency('CUP', '192', 'Cuban Peso', ['CUBA'])
CVE = add_currency('CVE', '132', 'Cape Verde Escudo', ['CAPE VERDE'])
CZK = add_currency('CZK', '203', 'Czech Koruna', ['CZECH REPUBLIC'])
DJF = add_currency('DJF', '262', 'Djibouti Franc', ['DJIBOUTI'])
DKK = add_currency('DKK', '208', 'Danish Krone', ['DENMARK', 'FAROE ISLANDS', 'GREENLAND'])
DOP = add_currency('DOP', '214', 'Dominican Peso', ['DOMINICAN REPUBLIC'])
DZD = add_currency('DZD', '012', 'Algerian Dinar', ['ALGERIA'])
EGP = add_currency('EGP', '818', 'Egyptian Pound', ['EGYPT'])
ERN = add_currency('ERN', '232', 'Nakfa', ['ERITREA'])
ETB = add_currency('ETB', '230', 'Ethiopian Birr', ['ETHIOPIA'])
EUR = add_currency('EUR', '978', 'Euro', ['AKROTIRI AND DHEKELIA', 'ANDORRA', 'AUSTRIA', 'BELGIUM',
                                          'CYPRUS', 'ESTONIA', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE',
                                          'GUADELOUPE', 'IRELAND', 'ITALY', 'KOSOVO', 'LATVIA', 'LITHUANIA',
                                          'LUXEMBOURG', 'MALTA', 'MARTINIQUE', 'MAYOTTE', 'MONACO',
                                          'MONTENEGRO', 'NETHERLANDS', 'PORTUGAL', 'RÉUNION', 'SAINT BARTHÉLEMY',
                                          'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SLOVAKIA', 'SLOVENIA', 'SPAIN',
                                          'VATICAN CITY'])
FJD = add_currency('FJD', '242', 'Fiji Dollar', ['FIJI'])
FKP = add_currency('FKP', '238', 'Falkland Islands Pound', ['FALKLAND ISLANDS (MALVINAS)'])
GBP = add_currency('GBP', '826', 'Pound Sterling', ['UNITED KINGDOM'])
GEL = add_currency('GEL', '981', 'Lari', ['GEORGIA'])
GHS = add_currency('GHS', '936', 'Ghana Cedi', ['GHANA'])
GIP = add_currency('GIP', '292', 'Gibraltar Pound', ['GIBRALTAR'])
GMD = add_currency('GMD', '270', 'Dalasi', ['GAMBIA'])
GNF = add_currency('GNF', '324', 'Guinea Franc', ['GUINEA'])
GTQ = add_currency('GTQ', '320', 'Quetzal', ['GUATEMALA'])
GYD = add_currency('GYD', '328', 'Guyana Dollar', ['GUYANA'])
HKD = add_currency('HKD', '344', 'Hong Kong Dollar', ['HONG KONG'])
HNL = add_currency('HNL', '340', 'Lempira', ['HONDURAS'])
HRK = add_currency('HRK', '191', 'Croatian Kuna', ['CROATIA'])
HTG = add_currency('HTG', '332', 'Haitian gourde', ['HAITI'])
HUF = add_currency('HUF', '348', 'Forint', ['HUNGARY'])
IDR = add_currency('IDR', '360', 'Rupiah', ['INDONESIA'])
ILS = add_currency('ILS', '376', 'New Israeli Sheqel', ['ISRAEL'])
IMP = add_currency('IMP', 'Nil', 'Isle of Man Pound', ['ISLE OF MAN'])
INR = add_currency('INR', '356', 'Indian Rupee', ['INDIA'])
IQD = add_currency('IQD', '368', 'Iraqi Dinar', ['IRAQ'])
IRR = add_currency('IRR', '364', 'Iranian Rial', ['IRAN'])
ISK = add_currency('ISK', '352', 'Iceland Krona', ['ICELAND'])
JMD = add_currency('JMD', '388', 'Jamaican Dollar', ['JAMAICA'])
JOD = add_currency('JOD', '400', 'Jordanian Dinar', ['JORDAN'])
JPY = add_currency('JPY', '392', 'Yen', ['JAPAN'])
KES = add_currency('KES', '404', 'Kenyan Shilling', ['KENYA'])
KGS = add_currency('KGS', '417', 'Som', ['KYRGYZSTAN'])
KHR = add_currency('KHR', '116', 'Riel', ['CAMBODIA'])
KMF = add_currency('KMF', '174', 'Comoro Franc', ['COMOROS'])
KPW = add_currency('KPW', '408', 'North Korean Won', ['KOREA'])
KRW = add_currency('KRW', '410', 'Won', ['KOREA'])
KWD = add_currency('KWD', '414', 'Kuwaiti Dinar', ['KUWAIT'])
KYD = add_currency('KYD', '136', 'Cayman Islands Dollar', ['CAYMAN ISLANDS'])
KZT = add_currency('KZT', '398', 'Tenge', ['KAZAKHSTAN'])
LAK = add_currency('LAK', '418', 'Kip', ['LAO PEOPLES DEMOCRATIC REPUBLIC'])
LBP = add_currency('LBP', '422', 'Lebanese Pound', ['LEBANON'])
LKR = add_currency('LKR', '144', 'Sri Lanka Rupee', ['SRI LANKA'])
LRD = add_currency('LRD', '430', 'Liberian Dollar', ['LIBERIA'])
LSL = add_currency('LSL', '426', 'Lesotho loti', ['LESOTHO'])
LTL = add_currency('LTL', '440', 'Lithuanian Litas', ['LITHUANIA'])
LVL = add_currency('LVL', '428', 'Latvian Lats', ['LATVIA'])
LYD = add_currency('LYD', '434', 'Libyan Dinar', ['LIBYAN ARAB JAMAHIRIYA'])
MAD = add_currency('MAD', '504', 'Moroccan Dirham', ['MOROCCO', 'WESTERN SAHARA'])
MDL = add_currency('MDL', '498', 'Moldovan Leu', ['MOLDOVA'])
MGA = add_currency('MGA', '969', 'Malagasy Ariary', ['MADAGASCAR'])
MKD = add_currency('MKD', '807', 'Denar', ['MACEDONIA'])
MMK = add_currency('MMK', '104', 'Kyat', ['MYANMAR'])
MNT = add_currency('MNT', '496', 'Tugrik', ['MONGOLIA'])
MOP = add_currency('MOP', '446', 'Pataca', ['MACAO'])
MRO = add_currency('MRO', '478', 'Ouguiya', ['MAURITANIA'])
MUR = add_currency('MUR', '480', 'Mauritius Rupee', ['MAURITIUS'])
MVR = add_currency('MVR', '462', 'Rufiyaa', ['MALDIVES'])
MWK = add_currency('MWK', '454', 'Malawian Kwacha', ['MALAWI'])
MXN = add_currency('MXN', '484', 'Mexican peso', ['MEXICO'])
MXV = add_currency('MXV', '979', 'Mexican Unidad de Inversion (UDI)', ['MEXICO'])
MYR = add_currency('MYR', '458', 'Malaysian Ringgit', ['MALAYSIA'])
MZN = add_currency('MZN', '943', 'Metical', ['MOZAMBIQUE'])
NAD = add_currency('NAD', '516', 'Namibian Dollar', ['NAMIBIA'])
NGN = add_currency('NGN', '566', 'Naira', ['NIGERIA'])
NIO = add_currency('NIO', '558', 'Cordoba Oro', ['NICARAGUA'])
NOK = add_currency('NOK', '578', 'Norwegian Krone', ['BOUVET ISLAND', 'NORWAY', 'SVALBARD AND JAN MAYEN'])
NPR = add_currency('NPR', '524', 'Nepalese Rupee', ['NEPAL'])
NZD = add_currency('NZD', '554', 'New Zealand Dollar', ['COOK ISLANDS', 'NEW ZEALAND', 'NIUE', 'PITCAIRN', 'TOKELAU'])
OMR = add_currency('OMR', '512', 'Rial Omani', ['OMAN'])
PAB = add_currency('PAB', '590', 'Balboa', ['PANAMA'])
PEN = add_currency('PEN', '604', 'Nuevo Sol', ['PERU'])
PGK = add_currency('PGK', '598', 'Kina', ['PAPUA NEW GUINEA'])
PHP = add_currency('PHP', '608', 'Philippine Peso', ['PHILIPPINES'])
PKR = add_currency('PKR', '586', 'Pakistan Rupee', ['PAKISTAN'])
PLN = add_currency('PLN', '985', 'Zloty', ['POLAND'])
PYG = add_currency('PYG', '600', 'Guarani', ['PARAGUAY'])
QAR = add_currency('QAR', '634', 'Qatari Rial', ['QATAR'])
RON = add_currency('RON', '946', 'New Leu', ['ROMANIA'])
RSD = add_currency('RSD', '941', 'Serbian Dinar', ['SERBIA'])
RUB = add_currency('RUB', '643', 'Russian Ruble', ['RUSSIAN FEDERATION'])
RWF = add_currency('RWF', '646', 'Rwanda Franc', ['RWANDA'])
SAR = add_currency('SAR', '682', 'Saudi Riyal', ['SAUDI ARABIA'])
SBD = add_currency('SBD', '090', 'Solomon Islands Dollar', ['SOLOMON ISLANDS'])
SCR = add_currency('SCR', '690', 'Seychelles Rupee', ['SEYCHELLES'])
SDG = add_currency('SDG', '938', 'Sudanese Pound', ['SUDAN'])
SEK = add_currency('SEK', '752', 'Swedish Krona', ['SWEDEN'])
SGD = add_currency('SGD', '702', 'Singapore Dollar', ['SINGAPORE'])
SHP = add_currency('SHP', '654', 'Saint Helena Pound', ['SAINT HELENA'])
SLL = add_currency('SLL', '694', 'Leone', ['SIERRA LEONE'])
SOS = add_currency('SOS', '706', 'Somali Shilling', ['SOMALIA'])
SRD = add_currency('SRD', '968', 'Surinam Dollar', ['SURINAME'])
SSP = add_currency('SSP', '728', 'South Sudanese Pound', ['SOUTH SUDAN'])
STD = add_currency('STD', '678', 'Dobra', ['SAO TOME AND PRINCIPE'])
SVC = add_currency('SVC', '222', 'El Salvador Colon', ['EL SALVADOR'])
SYP = add_currency('SYP', '760', 'Syrian Pound', ['SYRIAN ARAB REPUBLIC'])
SZL = add_currency('SZL', '748', 'Lilangeni', ['SWAZILAND'])
THB = add_currency('THB', '764', 'Baht', ['THAILAND'])
TJS = add_currency('TJS', '972', 'Somoni', ['TAJIKISTAN'])
TMM = add_currency('TMM', '795', 'Manat', ['TURKMENISTAN'])
TMT = add_currency('TMT', '934', 'Turkmenistan New Manat', ['TURKMENISTAN'])
TND = add_currency('TND', '788', 'Tunisian Dinar', ['TUNISIA'])
TOP = add_currency('TOP', '776', 'Paanga', ['TONGA'])
TRY = add_currency('TRY', '949', 'Turkish Lira', ['TURKEY'])
TTD = add_currency('TTD', '780', 'Trinidad and Tobago Dollar', ['TRINIDAD AND TOBAGO'])
TVD = add_currency('TVD', 'Nil', 'Tuvalu dollar', ['TUVALU'])
TWD = add_currency('TWD', '901', 'New Taiwan Dollar', ['TAIWAN'])
TZS = add_currency('TZS', '834', 'Tanzanian Shilling', ['TANZANIA'])
UAH = add_currency('UAH', '980', 'Hryvnia', ['UKRAINE'])
UGX = add_currency('UGX', '800', 'Uganda Shilling', ['UGANDA'])
USD = add_currency('USD', '840', 'US Dollar', ['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY',
                                               'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA',
                                               'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO',
                                               'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES',
                                               'UNITED STATES MINOR OUTLYING ISLANDS',
                                               'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
USN = add_currency('USN', '997', 'US Dollar (Next day)', ['UNITED STATES OF AMERICA (THE)'])
UYI = add_currency('UYI', '940', 'Uruguay Peso en Unidades Indexadas (URUIURUI)', ['URUGUAY'])
UYU = add_currency('UYU', '858', 'Uruguayan peso', ['URUGUAY'])
UZS = add_currency('UZS', '860', 'Uzbekistan Sum', ['UZBEKISTAN'])
VEF = add_currency('VEF', '937', 'Bolivar Fuerte', ['VENEZUELA'])
VND = add_currency('VND', '704', 'Dong', ['VIET NAM'])
VUV = add_currency('VUV', '548', 'Vatu', ['VANUATU'])
WST = add_currency('WST', '882', 'Tala', ['SAMOA'])
XAF = add_currency('XAF', '950', 'CFA franc BEAC', ['CAMEROON', 'CENTRAL AFRICAN REPUBLIC',
                                                    'REPUBLIC OF THE CONGO', 'CHAD', 'EQUATORIAL GUINEA',
                                                    'GABON'])
XAG = add_currency('XAG', '961', 'Silver', [])
XAU = add_currency('XAU', '959', 'Gold', [])
XBA = add_currency('XBA', '955', 'Bond Markets Units European Composite Unit (EURCO)', [])
XBB = add_currency('XBB', '956', 'European Monetary Unit (E.M.U.-6)', [])
XBC = add_currency('XBC', '957', 'European Unit of Account 9(E.U.A.-9)', [])
XBD = add_currency('XBD', '958', 'European Unit of Account 17(E.U.A.-17)', [])
XCD = add_currency('XCD', '951', 'East Caribbean Dollar', ['ANGUILLA', 'ANTIGUA AND BARBUDA', 'DOMINICA',
                                                           'GRENADA', 'MONTSERRAT', 'SAINT KITTS AND NEVIS',
                                                           'SAINT LUCIA', 'SAINT VINCENT AND THE GRENADINES'])
XDR = add_currency('XDR', '960', 'SDR', ['INTERNATIONAL MONETARY FUND (I.M.F)'])
XFO = add_currency('XFO', 'Nil', 'Gold-Franc', [])
XFU = add_currency('XFU', 'Nil', 'UIC-Franc', [])
XOF = add_currency('XOF', '952', 'CFA Franc BCEAO', ['BENIN', 'BURKINA FASO', 'COTE D\'IVOIRE',
                                                     'GUINEA-BISSAU', 'MALI', 'NIGER', 'SENEGAL', 'TOGO'])
XPD = add_currency('XPD', '964', 'Palladium', [])
XPF = add_currency('XPF', '953', 'CFP Franc', ['FRENCH POLYNESIA', 'NEW CALEDONIA', 'WALLIS AND FUTUNA'])
XPT = add_currency('XPT', '962', 'Platinum', [])
XSU = add_currency('XSU', '994', 'Sucre', ['SISTEMA UNITARIO DE COMPENSACION REGIONAL DE PAGOS "SUCRE"'])
XTS = add_currency('XTS', '963', 'Codes specifically reserved for testing purposes', [])
XUA = add_currency('XUA', '965', 'ADB Unit of Account', ['MEMBER COUNTRIES OF THE AFRICAN DEVELOPMENT BANK GROUP'])
XXX = add_currency(
    'XXX',
    '999',
    'The codes assigned for transactions where no currency is involved',
    ['ZZ07_No_Currency'],
)
YER = add_currency('YER', '886', 'Yemeni Rial', ['YEMEN'])
ZAR = add_currency('ZAR', '710', 'Rand', ['SOUTH AFRICA'])
ZMK = add_currency('ZMK', '894', 'Zambian Kwacha', [])  # historical
ZMW = add_currency('ZMW', '967', 'Zambian Kwacha', ['ZAMBIA'])
ZWD = add_currency('ZWD', '716', 'Zimbabwe Dollar A/06', ['ZIMBABWE'])
ZWL = add_currency('ZWL', '932', 'Zimbabwe dollar A/09', ['ZIMBABWE'])
ZWN = add_currency('ZWN', '942', 'Zimbabwe dollar A/08', ['ZIMBABWE'])
