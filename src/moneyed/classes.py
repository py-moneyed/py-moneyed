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

    def __init__(self, code='', numeric='999', sub_unit=1, name='', countries=[]):
        self.code = code
        self.countries = countries
        self.name = name
        self.numeric = numeric
        self.sub_unit = sub_unit

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
        return self.__class__(
            amount=self.amount,
            currency=self.currency)

    def __neg__(self):
        return self.__class__(
            amount= -self.amount,
            currency=self.currency)

    def __add__(self, other):
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
            return self.__class__(
                amount=(self.amount * Decimal(str(other))),
                currency=self.currency)

    def __truediv__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise TypeError('Cannot divide two different currencies.')
            return self.amount / other.amount
        else:
            return self.__class__(
                amount=self.amount / Decimal(str(other)),
                currency=self.currency)

    def __abs__(self):
        return self.__class__(
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

    def get_amount_in_sub_unit(self):
        return self.currency.sub_unit * self.amount

# ____________________________________________________________________
# Definitions of ISO 4217 Currencies
# Source: http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm

CURRENCIES = {}


def add_currency(code, numeric, sub_unit, name, countries):
    global CURRENCIES
    CURRENCIES[code] = Currency(
        code=code,
        numeric=numeric,
        sub_unit=sub_unit,
        name=name,
        countries=countries)
    return CURRENCIES[code]


def get_currency(code):
    try:
        return CURRENCIES[code]
    except KeyError:
        raise CurrencyDoesNotExist(code)

DEFAULT_CURRENCY = add_currency(DEFAULT_CURRENCY_CODE, '999', 1, 'Default currency.', [])


AED = add_currency('AED', '784', 100, 'UAE Dirham', ['UNITED ARAB EMIRATES'])
AFN = add_currency('AFN', '971', 100, 'Afghani', ['AFGHANISTAN'])
ALL = add_currency('ALL', '008', 100, 'Lek', ['ALBANIA'])
AMD = add_currency('AMD', '051', 100, 'Armenian Dram', ['ARMENIA'])
ANG = add_currency('ANG', '532', 100, 'Netherlands Antillian Guilder', ['NETHERLANDS ANTILLES'])
AOA = add_currency('AOA', '973', 100, 'Kwanza', ['ANGOLA'])
ARS = add_currency('ARS', '032', 100, 'Argentine Peso', ['ARGENTINA'])
AUD = add_currency('AUD', '036', 100, 'Australian Dollar', ['AUSTRALIA', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'HEARD ISLAND AND MCDONALD ISLANDS', 'KIRIBATI', 'NAURU', 'NORFOLK ISLAND', 'TUVALU'])
AWG = add_currency('AWG', '533', 100, 'Aruban Guilder', ['ARUBA'])
AZN = add_currency('AZN', '944', 100, 'Azerbaijanian Manat', ['AZERBAIJAN'])
BAM = add_currency('BAM', '977', 100, 'Convertible Marks', ['BOSNIA AND HERZEGOVINA'])
BBD = add_currency('BBD', '052', 100, 'Barbados Dollar', ['BARBADOS'])
BDT = add_currency('BDT', '050', 100, 'Taka', ['BANGLADESH'])
BGN = add_currency('BGN', '975', 100, 'Bulgarian Lev', ['BULGARIA'])
BHD = add_currency('BHD', '048', 100, 'Bahraini Dinar', ['BAHRAIN'])
BIF = add_currency('BIF', '108', 100, 'Burundi Franc', ['BURUNDI'])
BMD = add_currency('BMD', '060', 100, 'Bermudian Dollar (customarily known as Bermuda Dollar)', ['BERMUDA'])
BND = add_currency('BND', '096', 100, 'Brunei Dollar', ['BRUNEI DARUSSALAM'])
BRL = add_currency('BRL', '986', 100, 'Brazilian Real', ['BRAZIL'])
BSD = add_currency('BSD', '044', 100, 'Bahamian Dollar', ['BAHAMAS'])
BTN = add_currency('BTN', '064', 100, 'Bhutanese ngultrum', ['BHUTAN'])
BWP = add_currency('BWP', '072', 100, 'Pula', ['BOTSWANA'])
BYR = add_currency('BYR', '974', 100, 'Belarussian Ruble', ['BELARUS'])
BZD = add_currency('BZD', '084', 100, 'Belize Dollar', ['BELIZE'])
CAD = add_currency('CAD', '124', 100, 'Canadian Dollar', ['CANADA'])
CDF = add_currency('CDF', '976', 100, 'Congolese franc', ['DEMOCRATIC REPUBLIC OF CONGO'])
CHF = add_currency('CHF', '756', 100, 'Swiss Franc', ['LIECHTENSTEIN'])
CLP = add_currency('CLP', '152', 100, 'Chilean peso', ['CHILE'])
CNY = add_currency('CNY', '156', 100, 'Yuan Renminbi', ['CHINA'])
COP = add_currency('COP', '170', 100, 'Colombian peso', ['COLOMBIA'])
CRC = add_currency('CRC', '188', 100, 'Costa Rican Colon', ['COSTA RICA'])
CUC = add_currency('CUC', '931', 100, 'Cuban convertible peso', ['CUBA'])
CUP = add_currency('CUP', '192', 100, 'Cuban Peso', ['CUBA'])
CVE = add_currency('CVE', '132', 100, 'Cape Verde Escudo', ['CAPE VERDE'])
CZK = add_currency('CZK', '203', 100, 'Czech Koruna', ['CZECH REPUBLIC'])
DJF = add_currency('DJF', '262', 100, 'Djibouti Franc', ['DJIBOUTI'])
DKK = add_currency('DKK', '208', 100, 'Danish Krone', ['DENMARK', 'FAROE ISLANDS', 'GREENLAND'])
DOP = add_currency('DOP', '214', 100, 'Dominican Peso', ['DOMINICAN REPUBLIC'])
DZD = add_currency('DZD', '012', 100, 'Algerian Dinar', ['ALGERIA'])
EEK = add_currency('EEK', '233', 100, 'Kroon', ['ESTONIA'])
EGP = add_currency('EGP', '818', 100, 'Egyptian Pound', ['EGYPT'])
ERN = add_currency('ERN', '232', 100, 'Nakfa', ['ERITREA'])
ETB = add_currency('ETB', '230', 100, 'Ethiopian Birr', ['ETHIOPIA'])
EUR = add_currency('EUR', '978', 100, 'Euro', ['ANDORRA', 'AUSTRIA', 'BELGIUM', 'FINLAND', 'FRANCE', 'FRENCH GUIANA', 'FRENCH SOUTHERN TERRITORIES', 'GERMANY', 'GREECE', 'GUADELOUPE', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'MARTINIQUE', 'MAYOTTE', 'MONACO', 'MONTENEGRO', 'NETHERLANDS', 'PORTUGAL', 'R.UNION', 'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SLOVAKIA', 'SLOVENIA', 'SPAIN'])
FJD = add_currency('FJD', '242', 100, 'Fiji Dollar', ['FIJI'])
FKP = add_currency('FKP', '238', 100, 'Falkland Islands Pound', ['FALKLAND ISLANDS (MALVINAS)'])
GBP = add_currency('GBP', '826', 100, 'Pound Sterling', ['UNITED KINGDOM'])
GEL = add_currency('GEL', '981', 100, 'Lari', ['GEORGIA'])
GHS = add_currency('GHS', '936', 100, 'Ghana Cedi', ['GHANA'])
GIP = add_currency('GIP', '292', 100, 'Gibraltar Pound', ['GIBRALTAR'])
GMD = add_currency('GMD', '270', 100, 'Dalasi', ['GAMBIA'])
GNF = add_currency('GNF', '324', 100, 'Guinea Franc', ['GUINEA'])
GTQ = add_currency('GTQ', '320', 100, 'Quetzal', ['GUATEMALA'])
GYD = add_currency('GYD', '328', 100, 'Guyana Dollar', ['GUYANA'])
HKD = add_currency('HKD', '344', 100, 'Hong Kong Dollar', ['HONG KONG'])
HNL = add_currency('HNL', '340', 100, 'Lempira', ['HONDURAS'])
HRK = add_currency('HRK', '191', 100, 'Croatian Kuna', ['CROATIA'])
HTG = add_currency('HTG', '332', 100, 'Haitian gourde', ['HAITI'])
HUF = add_currency('HUF', '348', 100, 'Forint', ['HUNGARY'])
IDR = add_currency('IDR', '360', 100, 'Rupiah', ['INDONESIA'])
ILS = add_currency('ILS', '376', 100, 'New Israeli Sheqel', ['ISRAEL'])
IMP = add_currency('IMP', 'Nil', 100, 'Isle of Man pount', ['ISLE OF MAN'])
INR = add_currency('INR', '356', 100, 'Indian Rupee', ['INDIA'])
IQD = add_currency('IQD', '368', 100, 'Iraqi Dinar', ['IRAQ'])
IRR = add_currency('IRR', '364', 100, 'Iranian Rial', ['IRAN'])
ISK = add_currency('ISK', '352', 100, 'Iceland Krona', ['ICELAND'])
JMD = add_currency('JMD', '388', 100, 'Jamaican Dollar', ['JAMAICA'])
JOD = add_currency('JOD', '400', 100, 'Jordanian Dinar', ['JORDAN'])
JPY = add_currency('JPY', '392', 1, 'Yen', ['JAPAN'])
KES = add_currency('KES', '404', 100, 'Kenyan Shilling', ['KENYA'])
KGS = add_currency('KGS', '417', 100, 'Som', ['KYRGYZSTAN'])
KHR = add_currency('KHR', '116', 100, 'Riel', ['CAMBODIA'])
KMF = add_currency('KMF', '174', 100, 'Comoro Franc', ['COMOROS'])
KPW = add_currency('KPW', '408', 100, 'North Korean Won', ['KOREA'])
KRW = add_currency('KRW', '410', 100, 'Won', ['KOREA'])
KWD = add_currency('KWD', '414', 1000, 'Kuwaiti Dinar', ['KUWAIT'])
KYD = add_currency('KYD', '136', 100, 'Cayman Islands Dollar', ['CAYMAN ISLANDS'])
KZT = add_currency('KZT', '398', 100, 'Tenge', ['KAZAKHSTAN'])
LAK = add_currency('LAK', '418', 100, 'Kip', ['LAO PEOPLES DEMOCRATIC REPUBLIC'])
LBP = add_currency('LBP', '422', 100, 'Lebanese Pound', ['LEBANON'])
LKR = add_currency('LKR', '144', 100, 'Sri Lanka Rupee', ['SRI LANKA'])
LRD = add_currency('LRD', '430', 100, 'Liberian Dollar', ['LIBERIA'])
LSL = add_currency('LSL', '426', 100, 'Lesotho loti', ['LESOTHO'])
LTL = add_currency('LTL', '440', 100, 'Lithuanian Litas', ['LITHUANIA'])
LVL = add_currency('LVL', '428', 100, 'Latvian Lats', ['LATVIA'])
LYD = add_currency('LYD', '434', 1000, 'Libyan Dinar', ['LIBYAN ARAB JAMAHIRIYA'])
MAD = add_currency('MAD', '504', 100, 'Moroccan Dirham', ['MOROCCO', 'WESTERN SAHARA'])
MDL = add_currency('MDL', '498', 100, 'Moldovan Leu', ['MOLDOVA'])
MGA = add_currency('MGA', '969', 5, 'Malagasy Ariary', ['MADAGASCAR'])
MKD = add_currency('MKD', '807', 100, 'Denar', ['MACEDONIA'])
MMK = add_currency('MMK', '104', 100, 'Kyat', ['MYANMAR'])
MNT = add_currency('MNT', '496', 100, 'Tugrik', ['MONGOLIA'])
MOP = add_currency('MOP', '446', 100, 'Pataca', ['MACAO'])
MRO = add_currency('MRO', '478', 5, 'Ouguiya', ['MAURITANIA'])
MUR = add_currency('MUR', '480', 100, 'Mauritius Rupee', ['MAURITIUS'])
MVR = add_currency('MVR', '462', 100, 'Rufiyaa', ['MALDIVES'])
MWK = add_currency('MWK', '454', 100, 'Kwacha', ['MALAWI'])
MXN = add_currency('MXN', '484', 100, 'Mexixan peso', ['MEXICO'])
MYR = add_currency('MYR', '458', 100, 'Malaysian Ringgit', ['MALAYSIA'])
MZN = add_currency('MZN', '943', 100, 'Metical', ['MOZAMBIQUE'])
NAD = add_currency('NAD', '516', 100, 'Namibian Dollar', ['NAMIBIA'])
NGN = add_currency('NGN', '566', 100, 'Naira', ['NIGERIA'])
NIO = add_currency('NIO', '558', 100, 'Cordoba Oro', ['NICARAGUA'])
NOK = add_currency('NOK', '578', 100, 'Norwegian Krone', ['BOUVET ISLAND', 'NORWAY', 'SVALBARD AND JAN MAYEN'])
NPR = add_currency('NPR', '524', 100, 'Nepalese Rupee', ['NEPAL'])
NZD = add_currency('NZD', '554', 100, 'New Zealand Dollar', ['COOK ISLANDS', ', prefix=None, suffix=NoneNEW ZEALAND', 'NIUE', 'PITCAIRN', 'TOKELAU'])
OMR = add_currency('OMR', '512', 1000, 'Rial Omani', ['OMAN'])
PEN = add_currency('PEN', '604', 100, 'Nuevo Sol', ['PERU'])
PGK = add_currency('PGK', '598', 100, 'Kina', ['PAPUA NEW GUINEA'])
PHP = add_currency('PHP', '608', 100, 'Philippine Peso', ['PHILIPPINES'])
PKR = add_currency('PKR', '586', 100, 'Pakistan Rupee', ['PAKISTAN'])
PLN = add_currency('PLN', '985', 100, 'Zloty', ['POLAND'])
PYG = add_currency('PYG', '600', 100, 'Guarani', ['PARAGUAY'])
QAR = add_currency('QAR', '634', 100, 'Qatari Rial', ['QATAR'])
RON = add_currency('RON', '946', 100, 'New Leu', ['ROMANIA'])
RSD = add_currency('RSD', '941', 100, 'Serbian Dinar', ['SERBIA'])
RUB = add_currency('RUB', '643', 100, 'Russian Ruble', ['RUSSIAN FEDERATION'])
RWF = add_currency('RWF', '646', 100, 'Rwanda Franc', ['RWANDA'])
SAR = add_currency('SAR', '682', 100, 'Saudi Riyal', ['SAUDI ARABIA'])
SBD = add_currency('SBD', '090', 100, 'Solomon Islands Dollar', ['SOLOMON ISLANDS'])
SCR = add_currency('SCR', '690', 100, 'Seychelles Rupee', ['SEYCHELLES'])
SDG = add_currency('SDG', '938', 100, 'Sudanese Pound', ['SUDAN'])
SEK = add_currency('SEK', '752', 100, 'Swedish Krona', ['SWEDEN'])
SGD = add_currency('SGD', '702', 100, 'Singapore Dollar', ['SINGAPORE'])
SHP = add_currency('SHP', '654', 100, 'Saint Helena Pound', ['SAINT HELENA'])
SLL = add_currency('SLL', '694', 100, 'Leone', ['SIERRA LEONE'])
SOS = add_currency('SOS', '706', 100, 'Somali Shilling', ['SOMALIA'])
SRD = add_currency('SRD', '968', 100, 'Surinam Dollar', ['SURINAME'])
STD = add_currency('STD', '678', 100, 'Dobra', ['SAO TOME AND PRINCIPE'])
SYP = add_currency('SYP', '760', 100, 'Syrian Pound', ['SYRIAN ARAB REPUBLIC'])
SZL = add_currency('SZL', '748', 100, 'Lilangeni', ['SWAZILAND'])
THB = add_currency('THB', '764', 100, 'Baht', ['THAILAND'])
TJS = add_currency('TJS', '972', 100, 'Somoni', ['TAJIKISTAN'])
TMM = add_currency('TMM', '795', 100, 'Manat', ['TURKMENISTAN'])
TND = add_currency('TND', '788', 1000, 'Tunisian Dinar', ['TUNISIA'])
TOP = add_currency('TOP', '776', 100, 'Paanga', ['TONGA'])
TRY = add_currency('TRY', '949', 100, 'Turkish Lira', ['TURKEY'])
TTD = add_currency('TTD', '780', 100, 'Trinidad and Tobago Dollar', ['TRINIDAD AND TOBAGO'])
TVD = add_currency('TVD', 'Nil', 100, 'Tuvalu dollar', ['TUVALU'])
TWD = add_currency('TWD', '901', 100, 'New Taiwan Dollar', ['TAIWAN'])
TZS = add_currency('TZS', '834', 100, 'Tanzanian Shilling', ['TANZANIA'])
UAH = add_currency('UAH', '980', 100, 'Hryvnia', ['UKRAINE'])
UGX = add_currency('UGX', '800', 100, 'Uganda Shilling', ['UGANDA'])
USD = add_currency('USD', '840', 100, 'US Dollar', ['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY', 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA', 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO', 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES', 'UNITED STATES MINOR OUTLYING ISLANDS', 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
UYU = add_currency('UYU', '858', 100, 'Uruguayan peso', ['URUGUAY'])
UZS = add_currency('UZS', '860', 100, 'Uzbekistan Sum', ['UZBEKISTAN'])
VEF = add_currency('VEF', '937', 100, 'Bolivar Fuerte', ['VENEZUELA'])
VND = add_currency('VND', '704', 10, 'Dong', ['VIET NAM'])
VUV = add_currency('VUV', '548', 1, 'Vatu', ['VANUATU'])
WST = add_currency('WST', '882', 100, 'Tala', ['SAMOA'])
XAF = add_currency('XAF', '950', 100, 'CFA franc BEAC', ['CAMEROON', 'CENTRAL AFRICAN REPUBLIC', 'REPUBLIC OF THE CONGO', 'CHAD', 'EQUATORIAL GUINEA', 'GABON'])
XAG = add_currency('XAG', '961', 100, 'Silver', [])
XAU = add_currency('XAU', '959', 100, 'Gold', [])
XBA = add_currency('XBA', '955', 100, 'Bond Markets Units European Composite Unit (EURCO)', [])
XBB = add_currency('XBB', '956', 100, 'European Monetary Unit (E.M.U.-6)', [])
XBC = add_currency('XBC', '957', 100, 'European Unit of Account 9(E.U.A.-9)', [])
XBD = add_currency('XBD', '958', 100, 'European Unit of Account 17(E.U.A.-17)', [])
XCD = add_currency('XCD', '951', 100, 'East Caribbean Dollar', ['ANGUILLA', 'ANTIGUA AND BARBUDA', 'DOMINICA', 'GRENADA', 'MONTSERRAT', 'SAINT KITTS AND NEVIS', 'SAINT LUCIA', 'SAINT VINCENT AND THE GRENADINES'])
XDR = add_currency('XDR', '960', 100, 'SDR', ['INTERNATIONAL MONETARY FUND (I.M.F)'])
XFO = add_currency('XFO', 'Nil', 100, 'Gold-Franc', [])
XFU = add_currency('XFU', 'Nil', 100, 'UIC-Franc', [])
XOF = add_currency('XOF', '952', 100, 'CFA Franc BCEAO', ['BENIN', 'BURKINA FASO', 'COTE D\'IVOIRE', 'GUINEA-BISSAU', 'MALI', 'NIGER', 'SENEGAL', 'TOGO'])
XPD = add_currency('XPD', '964', 100, 'Palladium', [])
XPF = add_currency('XPF', '953', 100, 'CFP Franc', ['FRENCH POLYNESIA', 'NEW CALEDONIA', 'WALLIS AND FUTUNA'])
XPT = add_currency('XPT', '962', 100, 'Platinum', [])
XTS = add_currency('XTS', '963', 100, 'Codes specifically reserved for testing purposes', [])
YER = add_currency('YER', '886', 100, 'Yemeni Rial', ['YEMEN'])
ZAR = add_currency('ZAR', '710', 100, 'Rand', ['SOUTH AFRICA'])
ZMK = add_currency('ZMK', '894', 100, 'Kwacha', ['ZAMBIA'])
ZWD = add_currency('ZWD', '716', 100, 'Zimbabwe Dollar A/06', ['ZIMBABWE'])
ZWL = add_currency('ZWL', '932', 100, 'Zimbabwe dollar A/09', ['ZIMBABWE'])
ZWN = add_currency('ZWN', '942', 100, 'Zimbabwe dollar A/08', ['ZIMBABWE'])
