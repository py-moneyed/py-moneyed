# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from decimal import Decimal, ROUND_DOWN

# Default, non-existent, currency
DEFAULT_CURRENCY_CODE = 'XYZ'


class Currency(object):
    """
    A Currency represents a form of money issued by governments, and
    used in one or more states/countries.  A Currency instance
    encapsulates the related data of: the ISO currency/numeric code, a
    canonical name, countries the currency is used in, and an exchange
    rate - the last remains unimplemented however.
    """

    def __init__(self, code='', numeric='999', name='', countries=[], decimal_places=2):
        self.code = code
        self.countries = countries
        self.name = name
        self.numeric = numeric
        self.decimal_places = decimal_places

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
        return "%s %s" % (self.amount.to_integral_value(ROUND_DOWN),
                          self.currency)

    def __unicode__(self):
        from moneyed.localization import format_money
        return format_money(self)

    def __str__(self):
        from moneyed.localization import format_money
        return format_money(self)

    def __pos__(self):
        return Money(
            amount=self.amount,
            currency=self.currency)

    def __neg__(self):
        return Money(
            amount= -self.amount,
            currency=self.currency)

    def __add__(self, other):
        if not isinstance(other, Money):
            raise TypeError('Cannot add or subtract a ' +
                            'Money and non-Money instance.')
        if self.currency == other.currency:
            return Money(
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
            return Money(
                amount=(self.amount * Decimal(str(other))),
                currency=self.currency)

    def __truediv__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise TypeError('Cannot divide two different currencies.')
            return self.amount / other.amount
        else:
            return Money(
                amount=self.amount / Decimal(str(other)),
                currency=self.currency)

    def __abs__(self):
        return Money(
            amount=abs(self.amount),
            currency=self.currency)

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
            return Money(
                amount=(Decimal(str(other)) * self.amount / 100),
                currency=self.currency)

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rtruediv__ = __truediv__

    # _______________________________________
    # Override comparison operators
    def __eq__(self, other):
        return isinstance(other, Money)\
               and (self.amount == other.amount) \
               and (self.currency == other.currency)

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
# Source: https://es.wikipedia.org/wiki/ISO_4217

CURRENCIES = {}


def add_currency(code, numeric, name, countries, decimal_places):
    global CURRENCIES
    CURRENCIES[code] = Currency(
        code=code,
        numeric=numeric,
        name=name,
        countries=countries,
        decimal_places=decimal_places)
    return CURRENCIES[code]


def get_currency(code):
    try:
        return CURRENCIES[code]
    except KeyError:
        raise CurrencyDoesNotExist(code)


DEFAULT_CURRENCY = add_currency(DEFAULT_CURRENCY_CODE, '999', 'Default currency.', [], 2)


AED = add_currency('AED', '784', 'UAE Dirham', ['UNITED ARAB EMIRATES'], 2)
AFN = add_currency('AFN', '971', 'Afghani', ['AFGHANISTAN'], 2)
ALL = add_currency('ALL', '008', 'Lek', ['ALBANIA'], 2)
AMD = add_currency('AMD', '051', 'Armenian Dram', ['ARMENIA'], 2)
ANG = add_currency('ANG', '532', 'Netherlands Antillian Guilder', ['NETHERLANDS ANTILLES'], 2)
AOA = add_currency('AOA', '973', 'Kwanza', ['ANGOLA'], 2)
ARS = add_currency('ARS', '032', 'Argentine Peso', ['ARGENTINA'], 2)
AUD = add_currency('AUD', '036', 'Australian Dollar', ['AUSTRALIA', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'HEARD ISLAND AND MCDONALD ISLANDS', 'KIRIBATI', 'NAURU', 'NORFOLK ISLAND', 'TUVALU'], 2)
AWG = add_currency('AWG', '533', 'Aruban Guilder', ['ARUBA'], 2)
AZN = add_currency('AZN', '944', 'Azerbaijanian Manat', ['AZERBAIJAN'], 2)
BAM = add_currency('BAM', '977', 'Convertible Marks', ['BOSNIA AND HERZEGOVINA'], 2)
BBD = add_currency('BBD', '052', 'Barbados Dollar', ['BARBADOS'], 2)
BDT = add_currency('BDT', '050', 'Taka', ['BANGLADESH'], 2)
BGN = add_currency('BGN', '975', 'Bulgarian Lev', ['BULGARIA'], 2)
BHD = add_currency('BHD', '048', 'Bahraini Dinar', ['BAHRAIN'], 3)
BIF = add_currency('BIF', '108', 'Burundi Franc', ['BURUNDI'], 0)
BMD = add_currency('BMD', '060', 'Bermudian Dollar (customarily known as Bermuda Dollar)', ['BERMUDA'], 2)
BND = add_currency('BND', '096', 'Brunei Dollar', ['BRUNEI DARUSSALAM'], 2)
BRL = add_currency('BRL', '986', 'Brazilian Real', ['BRAZIL'], 2)
BSD = add_currency('BSD', '044', 'Bahamian Dollar', ['BAHAMAS'], 2)
BTN = add_currency('BTN', '064', 'Bhutanese ngultrum', ['BHUTAN'], 2)
BWP = add_currency('BWP', '072', 'Pula', ['BOTSWANA'], 2)
BYR = add_currency('BYR', '974', 'Belarussian Ruble', ['BELARUS'], 0)
BZD = add_currency('BZD', '084', 'Belize Dollar', ['BELIZE'], 2)
CAD = add_currency('CAD', '124', 'Canadian Dollar', ['CANADA'], 2)
CDF = add_currency('CDF', '976', 'Congolese franc', ['DEMOCRATIC REPUBLIC OF CONGO'], 2)
CHF = add_currency('CHF', '756', 'Swiss Franc', ['LIECHTENSTEIN'], 2)
CLP = add_currency('CLP', '152', 'Chilean peso', ['CHILE'], 0)
CNY = add_currency('CNY', '156', 'Yuan Renminbi', ['CHINA'], 2)
COP = add_currency('COP', '170', 'Colombian peso', ['COLOMBIA'], 2)
CRC = add_currency('CRC', '188', 'Costa Rican Colon', ['COSTA RICA'], 2)
CUC = add_currency('CUC', '931', 'Cuban convertible peso', ['CUBA'], 2)
CUP = add_currency('CUP', '192', 'Cuban Peso', ['CUBA'], 2)
CVE = add_currency('CVE', '132', 'Cape Verde Escudo', ['CAPE VERDE'], 2)
CZK = add_currency('CZK', '203', 'Czech Koruna', ['CZECH REPUBLIC'], 2)
DJF = add_currency('DJF', '262', 'Djibouti Franc', ['DJIBOUTI'], 0)
DKK = add_currency('DKK', '208', 'Danish Krone', ['DENMARK', 'FAROE ISLANDS', 'GREENLAND'], 2)
DOP = add_currency('DOP', '214', 'Dominican Peso', ['DOMINICAN REPUBLIC'], 2)
DZD = add_currency('DZD', '012', 'Algerian Dinar', ['ALGERIA'], 2)
EEK = add_currency('EEK', '233', 'Kroon', ['ESTONIA'], 2)
EGP = add_currency('EGP', '818', 'Egyptian Pound', ['EGYPT'], 2)
ERN = add_currency('ERN', '232', 'Nakfa', ['ERITREA'], 2)
ETB = add_currency('ETB', '230', 'Ethiopian Birr', ['ETHIOPIA'], 2)
EUR = add_currency('EUR', '978', 'Euro', ['ANDORRA', 'AUSTRIA', 'BELGIUM', 'FINLAND', 'FRANCE', 'FRENCH GUIANA', 'FRENCH SOUTHERN TERRITORIES', 'GERMANY', 'GREECE', 'GUADELOUPE', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'MARTINIQUE', 'MAYOTTE', 'MONACO', 'MONTENEGRO', 'NETHERLANDS', 'PORTUGAL', 'R.UNION', 'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SLOVAKIA', 'SLOVENIA', 'SPAIN'], 2)
FJD = add_currency('FJD', '242', 'Fiji Dollar', ['FIJI'], 2)
FKP = add_currency('FKP', '238', 'Falkland Islands Pound', ['FALKLAND ISLANDS (MALVINAS)'], 2)
GBP = add_currency('GBP', '826', 'Pound Sterling', ['UNITED KINGDOM'], 2)
GEL = add_currency('GEL', '981', 'Lari', ['GEORGIA'], 2)
GHS = add_currency('GHS', '936', 'Ghana Cedi', ['GHANA'], 2)
GIP = add_currency('GIP', '292', 'Gibraltar Pound', ['GIBRALTAR'], 2)
GMD = add_currency('GMD', '270', 'Dalasi', ['GAMBIA'], 2)
GNF = add_currency('GNF', '324', 'Guinea Franc', ['GUINEA'], 0)
GTQ = add_currency('GTQ', '320', 'Quetzal', ['GUATEMALA'], 2)
GYD = add_currency('GYD', '328', 'Guyana Dollar', ['GUYANA'], 2)
HKD = add_currency('HKD', '344', 'Hong Kong Dollar', ['HONG KONG'], 2)
HNL = add_currency('HNL', '340', 'Lempira', ['HONDURAS'], 2)
HRK = add_currency('HRK', '191', 'Croatian Kuna', ['CROATIA'], 2)
HTG = add_currency('HTG', '332', 'Haitian gourde', ['HAITI'], 2)
HUF = add_currency('HUF', '348', 'Forint', ['HUNGARY'], 0)
IDR = add_currency('IDR', '360', 'Rupiah', ['INDONESIA'], 2)
ILS = add_currency('ILS', '376', 'New Israeli Sheqel', ['ISRAEL'], 2)
IMP = add_currency('IMP', 'Nil', 'Isle of Man pount', ['ISLE OF MAN'], 2)
INR = add_currency('INR', '356', 'Indian Rupee', ['INDIA'], 2)
IQD = add_currency('IQD', '368', 'Iraqi Dinar', ['IRAQ'], 3)
IRR = add_currency('IRR', '364', 'Iranian Rial', ['IRAN'], 2)
ISK = add_currency('ISK', '352', 'Iceland Krona', ['ICELAND'], 0)
JMD = add_currency('JMD', '388', 'Jamaican Dollar', ['JAMAICA'], 2)
JOD = add_currency('JOD', '400', 'Jordanian Dinar', ['JORDAN'], 3)
JPY = add_currency('JPY', '392', 'Yen', ['JAPAN'], 0)
KES = add_currency('KES', '404', 'Kenyan Shilling', ['KENYA'], 2)
KGS = add_currency('KGS', '417', 'Som', ['KYRGYZSTAN'], 2)
KHR = add_currency('KHR', '116', 'Riel', ['CAMBODIA'], 2)
KMF = add_currency('KMF', '174', 'Comoro Franc', ['COMOROS'], 0)
KPW = add_currency('KPW', '408', 'North Korean Won', ['KOREA'], 2)
KRW = add_currency('KRW', '410', 'Won', ['KOREA'], 0)
KWD = add_currency('KWD', '414', 'Kuwaiti Dinar', ['KUWAIT'], 3)
KYD = add_currency('KYD', '136', 'Cayman Islands Dollar', ['CAYMAN ISLANDS'], 2)
KZT = add_currency('KZT', '398', 'Tenge', ['KAZAKHSTAN'], 2)
LAK = add_currency('LAK', '418', 'Kip', ['LAO PEOPLES DEMOCRATIC REPUBLIC'], 2)
LBP = add_currency('LBP', '422', 'Lebanese Pound', ['LEBANON'], 2)
LKR = add_currency('LKR', '144', 'Sri Lanka Rupee', ['SRI LANKA'], 2)
LRD = add_currency('LRD', '430', 'Liberian Dollar', ['LIBERIA'], 2)
LSL = add_currency('LSL', '426', 'Lesotho loti', ['LESOTHO'], 2)
LTL = add_currency('LTL', '440', 'Lithuanian Litas', ['LITHUANIA'], 2)
LVL = add_currency('LVL', '428', 'Latvian Lats', ['LATVIA'], 2)
LYD = add_currency('LYD', '434', 'Libyan Dinar', ['LIBYAN ARAB JAMAHIRIYA'], 3)
MAD = add_currency('MAD', '504', 'Moroccan Dirham', ['MOROCCO', 'WESTERN SAHARA'], 2)
MDL = add_currency('MDL', '498', 'Moldovan Leu', ['MOLDOVA'], 2)
MGA = add_currency('MGA', '969', 'Malagasy Ariary', ['MADAGASCAR'], 0)
MKD = add_currency('MKD', '807', 'Denar', ['MACEDONIA'], 2)
MMK = add_currency('MMK', '104', 'Kyat', ['MYANMAR'], 2)
MNT = add_currency('MNT', '496', 'Tugrik', ['MONGOLIA'], 2)
MOP = add_currency('MOP', '446', 'Pataca', ['MACAO'], 2)
MRO = add_currency('MRO', '478', 'Ouguiya', ['MAURITANIA'], 2)
MUR = add_currency('MUR', '480', 'Mauritius Rupee', ['MAURITIUS'], 2)
MVR = add_currency('MVR', '462', 'Rufiyaa', ['MALDIVES'], 2)
MWK = add_currency('MWK', '454', 'Kwacha', ['MALAWI'], 2)
MXN = add_currency('MXN', '484', 'Mexixan peso', ['MEXICO'], 2)
MYR = add_currency('MYR', '458', 'Malaysian Ringgit', ['MALAYSIA'], 2)
MZN = add_currency('MZN', '943', 'Metical', ['MOZAMBIQUE'], 0)
NAD = add_currency('NAD', '516', 'Namibian Dollar', ['NAMIBIA'], 2)
NGN = add_currency('NGN', '566', 'Naira', ['NIGERIA'], 2)
NIO = add_currency('NIO', '558', 'Cordoba Oro', ['NICARAGUA'], 2)
NOK = add_currency('NOK', '578', 'Norwegian Krone', ['BOUVET ISLAND', 'NORWAY', 'SVALBARD AND JAN MAYEN'], 2)
NPR = add_currency('NPR', '524', 'Nepalese Rupee', ['NEPAL'], 2)
NZD = add_currency('NZD', '554', 'New Zealand Dollar', ['COOK ISLANDS', ', prefix=None, suffix=NoneNEW ZEALAND', 'NIUE', 'PITCAIRN', 'TOKELAU'], 2)
OMR = add_currency('OMR', '512', 'Rial Omani', ['OMAN'], 3)
PEN = add_currency('PEN', '604', 'Nuevo Sol', ['PERU'], 2)
PGK = add_currency('PGK', '598', 'Kina', ['PAPUA NEW GUINEA'], 2)
PHP = add_currency('PHP', '608', 'Philippine Peso', ['PHILIPPINES'], 2)
PKR = add_currency('PKR', '586', 'Pakistan Rupee', ['PAKISTAN'], 2)
PLN = add_currency('PLN', '985', 'Zloty', ['POLAND'], 2)
PYG = add_currency('PYG', '600', 'Guarani', ['PARAGUAY'], 0)
QAR = add_currency('QAR', '634', 'Qatari Rial', ['QATAR'], 2)
RON = add_currency('RON', '946', 'New Leu', ['ROMANIA'], 2)
RSD = add_currency('RSD', '941', 'Serbian Dinar', ['SERBIA'], 2)
RUB = add_currency('RUB', '643', 'Russian Ruble', ['RUSSIAN FEDERATION'], 2)
RWF = add_currency('RWF', '646', 'Rwanda Franc', ['RWANDA'], 0)
SAR = add_currency('SAR', '682', 'Saudi Riyal', ['SAUDI ARABIA'], 2)
SBD = add_currency('SBD', '090', 'Solomon Islands Dollar', ['SOLOMON ISLANDS'], 2)
SCR = add_currency('SCR', '690', 'Seychelles Rupee', ['SEYCHELLES'], 2)
SDG = add_currency('SDG', '938', 'Sudanese Pound', ['SUDAN'], 2)
SEK = add_currency('SEK', '752', 'Swedish Krona', ['SWEDEN'], 2)
SGD = add_currency('SGD', '702', 'Singapore Dollar', ['SINGAPORE'], 2)
SHP = add_currency('SHP', '654', 'Saint Helena Pound', ['SAINT HELENA'], 2)
SLL = add_currency('SLL', '694', 'Leone', ['SIERRA LEONE'], 2)
SOS = add_currency('SOS', '706', 'Somali Shilling', ['SOMALIA'], 2)
SRD = add_currency('SRD', '968', 'Surinam Dollar', ['SURINAME'], 2)
STD = add_currency('STD', '678', 'Dobra', ['SAO TOME AND PRINCIPE'], 2)
SYP = add_currency('SYP', '760', 'Syrian Pound', ['SYRIAN ARAB REPUBLIC'], 2)
SZL = add_currency('SZL', '748', 'Lilangeni', ['SWAZILAND'], 2)
THB = add_currency('THB', '764', 'Baht', ['THAILAND'], 2)
TJS = add_currency('TJS', '972', 'Somoni', ['TAJIKISTAN'], 2)
TMM = add_currency('TMM', '795', 'Manat', ['TURKMENISTAN'], 2)
TND = add_currency('TND', '788', 'Tunisian Dinar', ['TUNISIA'], 3)
TOP = add_currency('TOP', '776', 'Paanga', ['TONGA'], 2)
TRY = add_currency('TRY', '949', 'Turkish Lira', ['TURKEY'], 2)
TTD = add_currency('TTD', '780', 'Trinidad and Tobago Dollar', ['TRINIDAD AND TOBAGO'], 2)
TVD = add_currency('TVD', 'Nil', 'Tuvalu dollar', ['TUVALU'], 2)
TWD = add_currency('TWD', '901', 'New Taiwan Dollar', ['TAIWAN'], 2)
TZS = add_currency('TZS', '834', 'Tanzanian Shilling', ['TANZANIA'], 2)
UAH = add_currency('UAH', '980', 'Hryvnia', ['UKRAINE'], 2)
UGX = add_currency('UGX', '800', 'Uganda Shilling', ['UGANDA'], 0)
USD = add_currency('USD', '840', 'US Dollar', ['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY', 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA', 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO', 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES', 'UNITED STATES MINOR OUTLYING ISLANDS', 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'], 2)
UYU = add_currency('UYU', '858', 'Uruguayan peso', ['URUGUAY'], 2)
UZS = add_currency('UZS', '860', 'Uzbekistan Sum', ['UZBEKISTAN'], 2)
VEF = add_currency('VEF', '937', 'Bolivar Fuerte', ['VENEZUELA'], 2)
VND = add_currency('VND', '704', 'Dong', ['VIET NAM'], 2)
VUV = add_currency('VUV', '548', 'Vatu', ['VANUATU'], 0)
WST = add_currency('WST', '882', 'Tala', ['SAMOA'], 2)
XAF = add_currency('XAF', '950', 'CFA franc BEAC', ['CAMEROON', 'CENTRAL AFRICAN REPUBLIC', 'REPUBLIC OF THE CONGO', 'CHAD', 'EQUATORIAL GUINEA', 'GABON'], 2)
XAG = add_currency('XAG', '961', 'Silver', [], 2)
XAU = add_currency('XAU', '959', 'Gold', [], 2)
XBA = add_currency('XBA', '955', 'Bond Markets Units European Composite Unit (EURCO)', [], 2)
XBB = add_currency('XBB', '956', 'European Monetary Unit (E.M.U.-6)', [], 2)
XBC = add_currency('XBC', '957', 'European Unit of Account 9(E.U.A.-9)', [], 2)
XBD = add_currency('XBD', '958', 'European Unit of Account 17(E.U.A.-17)', [], 2)
XCD = add_currency('XCD', '951', 'East Caribbean Dollar', ['ANGUILLA', 'ANTIGUA AND BARBUDA', 'DOMINICA', 'GRENADA', 'MONTSERRAT', 'SAINT KITTS AND NEVIS', 'SAINT LUCIA', 'SAINT VINCENT AND THE GRENADINES'], 2)
XDR = add_currency('XDR', '960', 'SDR', ['INTERNATIONAL MONETARY FUND (I.M.F)'], 2)
XFO = add_currency('XFO', 'Nil', 'Gold-Franc', [], 2)
XFU = add_currency('XFU', 'Nil', 'UIC-Franc', [], 2)
XOF = add_currency('XOF', '952', 'CFA Franc BCEAO', ['BENIN', 'BURKINA FASO', 'COTE D\'IVOIRE', 'GUINEA-BISSAU', 'MALI', 'NIGER', 'SENEGAL', 'TOGO'], 2)
XPD = add_currency('XPD', '964', 'Palladium', [], 2)
XPF = add_currency('XPF', '953', 'CFP Franc', ['FRENCH POLYNESIA', 'NEW CALEDONIA', 'WALLIS AND FUTUNA'], 2)
XPT = add_currency('XPT', '962', 'Platinum', [], 2)
XTS = add_currency('XTS', '963', 'Codes specifically reserved for testing purposes', [], 2)
YER = add_currency('YER', '886', 'Yemeni Rial', ['YEMEN'], 2)
ZAR = add_currency('ZAR', '710', 'Rand', ['SOUTH AFRICA'], 2)
ZMK = add_currency('ZMK', '894', 'Kwacha', ['ZAMBIA'], 2)
ZWD = add_currency('ZWD', '716', 'Zimbabwe Dollar A/06', ['ZIMBABWE'], 2)
ZWL = add_currency('ZWL', '932', 'Zimbabwe dollar A/09', ['ZIMBABWE'], 2)
ZWN = add_currency('ZWN', '942', 'Zimbabwe dollar A/08', ['ZIMBABWE'], 2),
