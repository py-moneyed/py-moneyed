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
        return format_money(self)

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
            raise TypeError('Cannot add or subtract a '
                            'Money and non-Money instance.')
        if self.currency == other.currency:
            return self.__class__(
                amount=self.amount + other.amount,
                currency=self.currency)

        raise TypeError('Cannot add or subtract two Money '
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


def get_currency(code=None, iso=None):
    try:
        if iso:
            return CURRENCIES_BY_ISO[str(iso)]
        return CURRENCIES[code]
    except KeyError:
        raise CurrencyDoesNotExist(code)


iso_4217_currencies = (
    (DEFAULT_CURRENCY_CODE, '999', 'Default currency.', []),
    ('AED', '784', 'UAE Dirham', ['UNITED ARAB EMIRATES']),
    ('AFN', '971', 'Afghani', ['AFGHANISTAN']),
    ('ALL', '008', 'Lek', ['ALBANIA']),
    ('AMD', '051', 'Armenian Dram', ['ARMENIA']),
    ('ANG', '532', 'Netherlands Antillian Guilder', ['NETHERLANDS ANTILLES']),
    ('AOA', '973', 'Kwanza', ['ANGOLA']),
    ('ARS', '032', 'Argentine Peso', ['ARGENTINA']),
    ('AUD', '036', 'Australian Dollar', ['AUSTRALIA', 'CHRISTMAS ISLAND',
                                         'COCOS (KEELING) ISLANDS',
                                         'HEARD ISLAND AND MCDONALD ISLANDS',
                                         'KIRIBATI', 'NAURU', 'NORFOLK ISLAND',
                                         'TUVALU']),
    ('AWG', '533', 'Aruban Guilder', ['ARUBA']),
    ('AZN', '944', 'Azerbaijanian Manat', ['AZERBAIJAN']),
    ('BAM', '977', 'Convertible Marks', ['BOSNIA AND HERZEGOVINA']),
    ('BBD', '052', 'Barbados Dollar', ['BARBADOS']),
    ('BDT', '050', 'Taka', ['BANGLADESH']),
    ('BGN', '975', 'Bulgarian Lev', ['BULGARIA']),
    ('BHD', '048', 'Bahraini Dinar', ['BAHRAIN']),
    ('BIF', '108', 'Burundi Franc', ['BURUNDI']),
    ('BMD', '060', 'Bermudian Dollar (customarily known as Bermuda Dollar)',
            ['BERMUDA']),
    ('BND', '096', 'Brunei Dollar', ['BRUNEI DARUSSALAM']),
    ('BRL', '986', 'Brazilian Real', ['BRAZIL']),
    ('BSD', '044', 'Bahamian Dollar', ['BAHAMAS']),
    ('BTN', '064', 'Bhutanese ngultrum', ['BHUTAN']),
    ('BWP', '072', 'Pula', ['BOTSWANA']),
    ('BYR', '974', 'Belarussian Ruble', ['BELARUS']),
    ('BZD', '084', 'Belize Dollar', ['BELIZE']),
    ('CAD', '124', 'Canadian Dollar', ['CANADA']),
    ('CDF', '976', 'Congolese franc', ['DEMOCRATIC REPUBLIC OF CONGO']),
    ('CHF', '756', 'Swiss Franc', ['LIECHTENSTEIN']),
    ('CLP', '152', 'Chilean peso', ['CHILE']),
    ('CNY', '156', 'Yuan Renminbi', ['CHINA']),
    ('COP', '170', 'Colombian peso', ['COLOMBIA']),
    ('CRC', '188', 'Costa Rican Colon', ['COSTA RICA']),
    ('CUC', '931', 'Cuban convertible peso', ['CUBA']),
    ('CUP', '192', 'Cuban Peso', ['CUBA']),
    ('CVE', '132', 'Cape Verde Escudo', ['CAPE VERDE']),
    ('CZK', '203', 'Czech Koruna', ['CZECH REPUBLIC']),
    ('DJF', '262', 'Djibouti Franc', ['DJIBOUTI']),
    ('DKK', '208', 'Danish Krone', ['DENMARK', 'FAROE ISLANDS', 'GREENLAND']),
    ('DOP', '214', 'Dominican Peso', ['DOMINICAN REPUBLIC']),
    ('DZD', '012', 'Algerian Dinar', ['ALGERIA']),
    ('EGP', '818', 'Egyptian Pound', ['EGYPT']),
    ('ERN', '232', 'Nakfa', ['ERITREA']),
    ('ETB', '230', 'Ethiopian Birr', ['ETHIOPIA']),
    ('EUR', '978', 'Euro', ['AKROTIRI AND DHEKELIA', 'ANDORRA', 'AUSTRIA',
                            'BELGIUM', 'CYPRUS', 'ESTONIA', 'FINLAND', 'FRANCE',
                            'GERMANY', 'GREECE', 'GUADELOUPE', 'IRELAND', 'ITALY',
                            'KOSOVO', 'LATVIA', 'LITHUANIA', 'LUXEMBOURG', 'MALTA',
                            'MARTINIQUE', 'MAYOTTE', 'MONACO', 'MONTENEGRO',
                            'NETHERLANDS', 'PORTUGAL', 'RÉUNION', 'SAN MARINO',
                            'SAINT BARTHÉLEMY', 'SAINT PIERRE AND MIQUELON',
                            'SAN MARINO', 'SLOVAKIA', 'SLOVENIA', 'SPAIN',
                            'VATICAN CITY']),
    ('FJD', '242', 'Fiji Dollar', ['FIJI']),
    ('FKP', '238', 'Falkland Islands Pound', ['FALKLAND ISLANDS (MALVINAS)']),
    ('GBP', '826', 'Pound Sterling', ['UNITED KINGDOM']),
    ('GEL', '981', 'Lari', ['GEORGIA']),
    ('GHS', '936', 'Ghana Cedi', ['GHANA']),
    ('GIP', '292', 'Gibraltar Pound', ['GIBRALTAR']),
    ('GMD', '270', 'Dalasi', ['GAMBIA']),
    ('GNF', '324', 'Guinea Franc', ['GUINEA']),
    ('GTQ', '320', 'Quetzal', ['GUATEMALA']),
    ('GYD', '328', 'Guyana Dollar', ['GUYANA']),
    ('HKD', '344', 'Hong Kong Dollar', ['HONG KONG']),
    ('HNL', '340', 'Lempira', ['HONDURAS']),
    ('HRK', '191', 'Croatian Kuna', ['CROATIA']),
    ('HTG', '332', 'Haitian gourde', ['HAITI']),
    ('HUF', '348', 'Forint', ['HUNGARY']),
    ('IDR', '360', 'Rupiah', ['INDONESIA']),
    ('ILS', '376', 'New Israeli Sheqel', ['ISRAEL']),
    ('IMP', 'Nil', 'Isle of Man Pound', ['ISLE OF MAN']),
    ('INR', '356', 'Indian Rupee', ['INDIA']),
    ('IQD', '368', 'Iraqi Dinar', ['IRAQ']),
    ('IRR', '364', 'Iranian Rial', ['IRAN']),
    ('ISK', '352', 'Iceland Krona', ['ICELAND']),
    ('JMD', '388', 'Jamaican Dollar', ['JAMAICA']),
    ('JOD', '400', 'Jordanian Dinar', ['JORDAN']),
    ('JPY', '392', 'Yen', ['JAPAN']),
    ('KES', '404', 'Kenyan Shilling', ['KENYA']),
    ('KGS', '417', 'Som', ['KYRGYZSTAN']),
    ('KHR', '116', 'Riel', ['CAMBODIA']),
    ('KMF', '174', 'Comoro Franc', ['COMOROS']),
    ('KPW', '408', 'North Korean Won', ['KOREA']),
    ('KRW', '410', 'Won', ['KOREA']),
    ('KWD', '414', 'Kuwaiti Dinar', ['KUWAIT']),
    ('KYD', '136', 'Cayman Islands Dollar', ['CAYMAN ISLANDS']),
    ('KZT', '398', 'Tenge', ['KAZAKHSTAN']),
    ('LAK', '418', 'Kip', ['LAO PEOPLES DEMOCRATIC REPUBLIC']),
    ('LBP', '422', 'Lebanese Pound', ['LEBANON']),
    ('LKR', '144', 'Sri Lanka Rupee', ['SRI LANKA']),
    ('LRD', '430', 'Liberian Dollar', ['LIBERIA']),
    ('LSL', '426', 'Lesotho loti', ['LESOTHO']),
    ('LTL', '440', 'Lithuanian Litas', ['LITHUANIA']),
    ('LVL', '428', 'Latvian Lats', ['LATVIA']),
    ('LYD', '434', 'Libyan Dinar', ['LIBYAN ARAB JAMAHIRIYA']),
    ('MAD', '504', 'Moroccan Dirham', ['MOROCCO', 'WESTERN SAHARA']),
    ('MDL', '498', 'Moldovan Leu', ['MOLDOVA']),
    ('MGA', '969', 'Malagasy Ariary', ['MADAGASCAR']),
    ('MKD', '807', 'Denar', ['MACEDONIA']),
    ('MMK', '104', 'Kyat', ['MYANMAR']),
    ('MNT', '496', 'Tugrik', ['MONGOLIA']),
    ('MOP', '446', 'Pataca', ['MACAO']),
    ('MRO', '478', 'Ouguiya', ['MAURITANIA']),
    ('MUR', '480', 'Mauritius Rupee', ['MAURITIUS']),
    ('MVR', '462', 'Rufiyaa', ['MALDIVES']),
    ('MWK', '454', 'Malawian Kwacha', ['MALAWI']),
    ('MXN', '484', 'Mexican peso', ['MEXICO']),
    ('MYR', '458', 'Malaysian Ringgit', ['MALAYSIA']),
    ('MZN', '943', 'Metical', ['MOZAMBIQUE']),
    ('NAD', '516', 'Namibian Dollar', ['NAMIBIA']),
    ('NGN', '566', 'Naira', ['NIGERIA']),
    ('NIO', '558', 'Cordoba Oro', ['NICARAGUA']),
    ('NOK', '578', 'Norwegian Krone', ['BOUVET ISLAND', 'NORWAY',
                                       'SVALBARD AND JAN MAYEN']),
    ('NPR', '524', 'Nepalese Rupee', ['NEPAL']),
    ('NZD', '554', 'New Zealand Dollar', ['COOK ISLANDS', 'NEW ZEALAND',
                                          'NIUE', 'PITCAIRN', 'TOKELAU']),
    ('OMR', '512', 'Rial Omani', ['OMAN']),
    ('PEN', '604', 'Nuevo Sol', ['PERU']),
    ('PGK', '598', 'Kina', ['PAPUA NEW GUINEA']),
    ('PHP', '608', 'Philippine Peso', ['PHILIPPINES']),
    ('PKR', '586', 'Pakistan Rupee', ['PAKISTAN']),
    ('PLN', '985', 'Zloty', ['POLAND']),
    ('PYG', '600', 'Guarani', ['PARAGUAY']),
    ('QAR', '634', 'Qatari Rial', ['QATAR']),
    ('RON', '946', 'New Leu', ['ROMANIA']),
    ('RSD', '941', 'Serbian Dinar', ['SERBIA']),
    ('RUB', '643', 'Russian Ruble', ['RUSSIAN FEDERATION']),
    ('RWF', '646', 'Rwanda Franc', ['RWANDA']),
    ('SAR', '682', 'Saudi Riyal', ['SAUDI ARABIA']),
    ('SBD', '090', 'Solomon Islands Dollar', ['SOLOMON ISLANDS']),
    ('SCR', '690', 'Seychelles Rupee', ['SEYCHELLES']),
    ('SDG', '938', 'Sudanese Pound', ['SUDAN']),
    ('SEK', '752', 'Swedish Krona', ['SWEDEN']),
    ('SGD', '702', 'Singapore Dollar', ['SINGAPORE']),
    ('SHP', '654', 'Saint Helena Pound', ['SAINT HELENA']),
    ('SLL', '694', 'Leone', ['SIERRA LEONE']),
    ('SOS', '706', 'Somali Shilling', ['SOMALIA']),
    ('SRD', '968', 'Surinam Dollar', ['SURINAME']),
    ('STD', '678', 'Dobra', ['SAO TOME AND PRINCIPE']),
    ('SYP', '760', 'Syrian Pound', ['SYRIAN ARAB REPUBLIC']),
    ('SZL', '748', 'Lilangeni', ['SWAZILAND']),
    ('THB', '764', 'Baht', ['THAILAND']),
    ('TJS', '972', 'Somoni', ['TAJIKISTAN']),
    ('TMM', '795', 'Manat', ['TURKMENISTAN']),
    ('TND', '788', 'Tunisian Dinar', ['TUNISIA']),
    ('TOP', '776', 'Paanga', ['TONGA']),
    ('TRY', '949', 'Turkish Lira', ['TURKEY']),
    ('TTD', '780', 'Trinidad and Tobago Dollar', ['TRINIDAD AND TOBAGO']),
    ('TWD', '901', 'New Taiwan Dollar', ['TAIWAN']),
    ('TZS', '834', 'Tanzanian Shilling', ['TANZANIA']),
    ('UAH', '980', 'Hryvnia', ['UKRAINE']),
    ('UGX', '800', 'Uganda Shilling', ['UGANDA']),
    ('USD', '840', 'US Dollar', ['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY',
                                 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA',
                                 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO',
                                 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS',
                                 'UNITED STATES', 'UNITED STATES MINOR OUTLYING ISLANDS',
                                 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)']),
    ('UYU', '858', 'Uruguayan peso', ['URUGUAY']),
    ('UZS', '860', 'Uzbekistan Sum', ['UZBEKISTAN']),
    ('VEF', '937', 'Bolivar Fuerte', ['VENEZUELA']),
    ('VND', '704', 'Dong', ['VIET NAM']),
    ('VUV', '548', 'Vatu', ['VANUATU']),
    ('WST', '882', 'Tala', ['SAMOA']),
    ('XAF', '950', 'CFA franc BEAC', ['CAMEROON', 'CENTRAL AFRICAN REPUBLIC',
                                      'REPUBLIC OF THE CONGO', 'CHAD',
                                      'EQUATORIAL GUINEA', 'GABON']),
    ('XAG', '961', 'Silver', []),
    ('XAU', '959', 'Gold', []),
    ('XBA', '955', 'Bond Markets Units European Composite Unit (EURCO)', []),
    ('XBB', '956', 'European Monetary Unit (E.M.U.-6)', []),
    ('XBC', '957', 'European Unit of Account 9(E.U.A.-9)', []),
    ('XBD', '958', 'European Unit of Account 17(E.U.A.-17)', []),
    ('XCD', '951', 'East Caribbean Dollar', ['ANGUILLA', 'ANTIGUA AND BARBUDA',
                                             'DOMINICA', 'GRENADA', 'MONTSERRAT',
                                             'SAINT KITTS AND NEVIS', 'SAINT LUCIA',
                                             'SAINT VINCENT AND THE GRENADINES']),
    ('XDR', '960', 'SDR', ['INTERNATIONAL MONETARY FUND (I.M.F)']),
    ('XOF', '952', 'CFA Franc BCEAO', ['BENIN', 'BURKINA FASO', 'COTE D\'IVOIRE',
                                       'GUINEA-BISSAU', 'MALI', 'NIGER', 'SENEGAL',
                                       'TOGO']),
    ('XPD', '964', 'Palladium', []),
    ('XPF', '953', 'CFP Franc', ['FRENCH POLYNESIA', 'NEW CALEDONIA',
                                 'WALLIS AND FUTUNA']),
    ('XPT', '962', 'Platinum', []),
    ('XTS', '963', 'Codes specifically reserved for testing purposes', []),
    ('YER', '886', 'Yemeni Rial', ['YEMEN']),
    ('ZAR', '710', 'Rand', ['SOUTH AFRICA']),
    ('ZMK', '894', 'Zambian Kwacha', []),  # historical
    ('ZMW', '967', 'Zambian Kwacha', ['ZAMBIA']),
    ('ZWD', '716', 'Zimbabwe Dollar A/06', ['ZIMBABWE']),
    ('ZWL', '932', 'Zimbabwe dollar A/09', ['ZIMBABWE']),
    ('ZWN', '942', 'Zimbabwe dollar A/08', ['ZIMBABWE']),
)

CURRENCIES = {}
CURRENCIES_BY_ISO = {}

for iso_currency in iso_4217_currencies:
    temp = Currency(*iso_currency)
    CURRENCIES[iso_currency[0]] = temp
    CURRENCIES_BY_ISO[iso_currency[1]] = temp

DEFAULT_CURRENCY = CURRENCIES[DEFAULT_CURRENCY_CODE]
