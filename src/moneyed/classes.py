# -*- coding: utf-8 -*-

from decimal import Decimal

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
    exchange_rate = Decimal('1.0')

    def __init__(self, code='', numeric='999', name='', countries=[],
                 prefix=None, suffix=None):
        self.code = code
        self.countries = countries
        self.name = name
        self.numeric = numeric
        
        if suffix is None and prefix is None:
            suffix = code
        self.prefix = prefix or u''
        self.suffix = suffix

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
        super(CurrencyDoesNotExist, self).__init__(u"No currency with code %s is defined." % code)

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

    def __unicode__(self):
        return "%s %s" % (self.amount, self.currency)

    __repr__ = __unicode__

    def __pos__(self):
        return Money(
            amount=self.amount,
            currency=self.currency)

    def __neg__(self):
        return Money(
            amount=-self.amount,
            currency=self.currency)

    def __add__(self, other):
        if not isinstance(other, Money):
            raise TypeError('Cannot add a Money and non-Money instance.')
        if self.currency == other.currency:
            return Money(
                amount=self.amount + other.amount,
                currency=self.currency)
        else:
            this = self.convert_to_default()
            other = other.convert_to_default()
            return Money(
                amount=(this.amount + other.amount),
                currency=DEFAULT_CURRENCY_CODE)

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        if isinstance(other, Money):
            raise TypeError('Cannot multiply two Money instances.')
        else:
            return Money(
                amount=(self.amount * Decimal(str(other))),
                currency=self.currency)

    def __div__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise TypeError('Cannot divide two different currencies.')
            return self.amount / other.amount
        else:
            return Money(
                amount=self.amount / Decimal(str(other)),
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
    __rdiv__ = __div__

    # _______________________________________
    # Override comparison operators
    def __eq__(self, other):
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        return (self.amount == other.amount) \
               and (self.currency == other.currency)

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other):
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if (self.currency == other.currency):
            return (self.amount < other.amount)
        else:
            raise TypeError('Cannot compare different currencies (yet).')

    def __gt__(self, other):
        if not isinstance(other, Money):
            raise MoneyComparisonError(other)
        if (self.currency == other.currency):
            return (self.amount > other.amount)
        else:
            raise TypeError('Cannot compare different currencies (yet).')

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other


# ____________________________________________________________________
# Definitions of ISO 4217 Currencies
# Source: http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm

CURRENCIES = {}
def add_currency(code, numeric, name, countries, prefix=None, suffix=None):
    global CURRENCIES
    CURRENCIES[code] = Currency(
        code=code, 
        numeric=numeric, 
        name=name, 
        countries=countries,
        prefix=prefix,
        suffix=suffix)
    return CURRENCIES[code]
    
def get_currency(code):
    try:
        return CURRENCIES[code]
    except KeyError:
        raise CurrencyDoesNotExist(code)

add_currency('BZD', '084', 'Belize Dollar', ['BELIZE'])
add_currency('YER', '886', 'Yemeni Rial', ['YEMEN'])
add_currency('XBA', '955', 'Bond Markets Units European Composite Unit (EURCO)', [])
add_currency('SLL', '694', 'Leone', ['SIERRA LEONE'])
add_currency('ERN', '232', 'Nakfa', ['ERITREA'])
add_currency('NGN', '566', 'Naira', ['NIGERIA'])
add_currency('CRC', '188', 'Costa Rican Colon', ['COSTA RICA'])
add_currency('VEF', '937', 'Bolivar Fuerte', ['VENEZUELA'])
add_currency('LAK', '418', 'Kip', ['LAO PEOPLES DEMOCRATIC REPUBLIC'])
add_currency('DZD', '012', 'Algerian Dinar', ['ALGERIA'])
add_currency('SZL', '748', 'Lilangeni', ['SWAZILAND'])
add_currency('MOP', '446', 'Pataca', ['MACAO'])
add_currency('BYR', '974', 'Belarussian Ruble', ['BELARUS'])
add_currency('MUR', '480', 'Mauritius Rupee', ['MAURITIUS'])
add_currency('WST', '882', 'Tala', ['SAMOA'])
add_currency('LRD', '430', 'Liberian Dollar', ['LIBERIA'])
add_currency('MMK', '104', 'Kyat', ['MYANMAR'])
add_currency('KGS', '417', 'Som', ['KYRGYZSTAN'])
add_currency('PYG', '600', 'Guarani', ['PARAGUAY'])
add_currency('IDR', '360', 'Rupiah', ['INDONESIA'])
add_currency('XBD', '958', 'European Unit of Account 17(E.U.A.-17)', [])
add_currency('GTQ', '320', 'Quetzal', ['GUATEMALA'])
add_currency('CAD', '124', 'Canadian Dollar', ['CANADA'])
add_currency('AWG', '533', 'Aruban Guilder', ['ARUBA'])
add_currency('TTD', '780', 'Trinidad and Tobago Dollar', ['TRINIDAD AND TOBAGO'])
add_currency('PKR', '586', 'Pakistan Rupee', ['PAKISTAN'])
add_currency('XBC', '957', 'European Unit of Account 9(E.U.A.-9)', [])
add_currency('UZS', '860', 'Uzbekistan Sum', ['UZBEKISTAN'])
add_currency('XCD', '951', 'East Caribbean Dollar', ['ANGUILLA', 'ANTIGUA AND BARBUDA', 'DOMINICA', 'GRENADA', 'MONTSERRAT', 'SAINT KITTS AND NEVIS', 'SAINT LUCIA', 'SAINT VINCENT AND THE GRENADINES'])
add_currency('VUV', '548', 'Vatu', ['VANUATU'])
add_currency('KMF', '174', 'Comoro Franc', ['COMOROS'])
add_currency('AZN', '944', 'Azerbaijanian Manat', ['AZERBAIJAN'])
add_currency('XPD', '964', 'Palladium', [])
add_currency('MNT', '496', 'Tugrik', ['MONGOLIA'])
add_currency('ANG', '532', 'Netherlands Antillian Guilder', ['NETHERLANDS ANTILLES'])
add_currency('LBP', '422', 'Lebanese Pound', ['LEBANON'])
add_currency('KES', '404', 'Kenyan Shilling', ['KENYA'])
add_currency('GBP', '826', 'Pound Sterling', ['UNITED KINGDOM'])
add_currency('SEK', '752', 'Swedish Krona', ['SWEDEN'])
add_currency('AFN', '971', 'Afghani', ['AFGHANISTAN'])
add_currency('KZT', '398', 'Tenge', ['KAZAKHSTAN'])
add_currency('ZMK', '894', 'Kwacha', ['ZAMBIA'])
add_currency('SKK', '703', 'Slovak Koruna', ['SLOVAKIA'])
add_currency('DKK', '208', 'Danish Krone', ['DENMARK', 'FAROE ISLANDS', 'GREENLAND'])
add_currency('TMM', '795', 'Manat', ['TURKMENISTAN'])
add_currency('AMD', '051', 'Armenian Dram', ['ARMENIA'])
add_currency('SCR', '690', 'Seychelles Rupee', ['SEYCHELLES'])
add_currency('FJD', '242', 'Fiji Dollar', ['FIJI'])
add_currency('SHP', '654', 'Saint Helena Pound', ['SAINT HELENA'])
add_currency('ALL', '008', 'Lek', ['ALBANIA'])
add_currency('TOP', '776', 'Paanga', ['TONGA'])
add_currency('UGX', '800', 'Uganda Shilling', ['UGANDA'])
add_currency('OMR', '512', 'Rial Omani', ['OMAN'])
add_currency('DJF', '262', 'Djibouti Franc', ['DJIBOUTI'])
add_currency('BND', '096', 'Brunei Dollar', ['BRUNEI DARUSSALAM'])
add_currency('TND', '788', 'Tunisian Dinar', ['TUNISIA'])
add_currency('SBD', '090', 'Solomon Islands Dollar', ['SOLOMON ISLANDS'])
add_currency('GHS', '936', 'Ghana Cedi', ['GHANA'])
add_currency('GNF', '324', 'Guinea Franc', ['GUINEA'])
add_currency('CVE', '132', 'Cape Verde Escudo', ['CAPE VERDE'])
add_currency('ARS', '032', 'Argentine Peso', ['ARGENTINA'])
add_currency('GMD', '270', 'Dalasi', ['GAMBIA'])
add_currency('ZWD', '716', 'Zimbabwe Dollar', ['ZIMBABWE'])
add_currency('MWK', '454', 'Kwacha', ['MALAWI'])
add_currency('BDT', '050', 'Taka', ['BANGLADESH'])
add_currency('KWD', '414', 'Kuwaiti Dinar', ['KUWAIT'])
add_currency('EUR', '978', 'Euro', ['ANDORRA', 'AUSTRIA', 'BELGIUM', 'FINLAND', 'FRANCE', 'FRENCH GUIANA', 'FRENCH SOUTHERN TERRITORIES', 'GERMANY', 'GREECE', 'GUADELOUPE', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'MARTINIQUE', 'MAYOTTE', 'MONACO', 'MONTENEGRO', 'NETHERLANDS', 'PORTUGAL', 'R.UNION', 'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SLOVENIA', 'SPAIN'])
add_currency('CHF', '756', 'Swiss Franc', ['LIECHTENSTEIN'])
add_currency('XAG', '961', 'Silver', [])
add_currency('SRD', '968', 'Surinam Dollar', ['SURINAME'])
add_currency('DOP', '214', 'Dominican Peso', ['DOMINICAN REPUBLIC'])
add_currency('PEN', '604', 'Nuevo Sol', ['PERU'])
add_currency('KPW', '408', 'North Korean Won', ['KOREA'])
add_currency('SGD', '702', 'Singapore Dollar', ['SINGAPORE'])
add_currency('TWD', '901', 'New Taiwan Dollar', ['TAIWAN'])
add_currency('USD', '840', 'US Dollar', ['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY', 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA', 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO', 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES MINOR OUTLYING ISLANDS', 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
add_currency('BGN', '975', 'Bulgarian Lev', ['BULGARIA'])
add_currency('MAD', '504', 'Moroccan Dirham', ['MOROCCO', 'WESTERN SAHARA'])
add_currency('XXX', '999', 'The codes assigned for transactions where no currency is involved are:', [])
add_currency('SAR', '682', 'Saudi Riyal', ['SAUDI ARABIA'])
add_currency('AUD', '036', 'Australian Dollar', ['AUSTRALIA', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'HEARD ISLAND AND MCDONALD ISLANDS', 'KIRIBATI', 'NAURU', 'NORFOLK ISLAND', 'TUVALU'])
add_currency('KYD', '136', 'Cayman Islands Dollar', ['CAYMAN ISLANDS'])
add_currency('KRW', '410', 'Won', ['KOREA'])
add_currency('GIP', '292', 'Gibraltar Pound', ['GIBRALTAR'])
add_currency('TRY', '949', 'New Turkish Lira', ['TURKEY'])
add_currency('XAU', '959', 'Gold', [])
add_currency('CZK', '203', 'Czech Koruna', ['CZECH REPUBLIC'])
add_currency('JMD', '388', 'Jamaican Dollar', ['JAMAICA'])
add_currency('BSD', '044', 'Bahamian Dollar', ['BAHAMAS'])
add_currency('BWP', '072', 'Pula', ['BOTSWANA'])
add_currency('GYD', '328', 'Guyana Dollar', ['GUYANA'])
add_currency('XTS', '963', 'Codes specifically reserved for testing purposes', [])
add_currency('LYD', '434', 'Libyan Dinar', ['LIBYAN ARAB JAMAHIRIYA'])
add_currency('EGP', '818', 'Egyptian Pound', ['EGYPT'])
add_currency('THB', '764', 'Baht', ['THAILAND'])
add_currency('MKD', '807', 'Denar', ['MACEDONIA'])
add_currency('SDG', '938', 'Sudanese Pound', ['SUDAN'])
add_currency('AED', '784', 'UAE Dirham', ['UNITED ARAB EMIRATES'])
add_currency('JOD', '400', 'Jordanian Dinar', ['JORDAN'])
add_currency('JPY', '392', 'Yen', ['JAPAN'])
add_currency('ZAR', '710', 'Rand', ['SOUTH AFRICA'])
add_currency('HRK', '191', 'Croatian Kuna', ['CROATIA'])
add_currency('AOA', '973', 'Kwanza', ['ANGOLA'])
add_currency('RWF', '646', 'Rwanda Franc', ['RWANDA'])
add_currency('CUP', '192', 'Cuban Peso', ['CUBA'])
add_currency('XFO', 'Nil', 'Gold-Franc', [])
add_currency('BBD', '052', 'Barbados Dollar', ['BARBADOS'])
add_currency('PGK', '598', 'Kina', ['PAPUA NEW GUINEA'])
add_currency('LKR', '144', 'Sri Lanka Rupee', ['SRI LANKA'])
add_currency('RON', '946', 'New Leu', ['ROMANIA'])
add_currency('PLN', '985', 'Zloty', ['POLAND'])
add_currency('IQD', '368', 'Iraqi Dinar', ['IRAQ'])
add_currency('TJS', '972', 'Somoni', ['TAJIKISTAN'])
add_currency('MDL', '498', 'Moldovan Leu', ['MOLDOVA'])
add_currency('MYR', '458', 'Malaysian Ringgit', ['MALAYSIA'])
add_currency('CNY', '156', 'Yuan Renminbi', ['CHINA'])
add_currency('LVL', '428', 'Latvian Lats', ['LATVIA'])
add_currency('INR', '356', 'Indian Rupee', ['INDIA'])
add_currency('FKP', '238', 'Falkland Islands Pound', ['FALKLAND ISLANDS (MALVINAS)'])
add_currency('NIO', '558', 'Cordoba Oro', ['NICARAGUA'])
add_currency('PHP', '608', 'Philippine Peso', ['PHILIPPINES'])
add_currency('HNL', '340', 'Lempira', ['HONDURAS'])
add_currency('HKD', '344', 'Hong Kong Dollar', ['HONG KONG'])
add_currency('NZD', '554', 'New Zealand Dollar', ['COOK ISLANDS', 'NEW ZEALAND', 'NIUE', 'PITCAIRN', 'TOKELAU'])
add_currency('BRL', '986', 'Brazilian Real', ['BRAZIL'])
add_currency('RSD', '941', 'Serbian Dinar', ['SERBIA'])
add_currency('XBB', '956', 'European Monetary Unit (E.M.U.-6)', [])
add_currency('EEK', '233', 'Kroon', ['ESTONIA'])
add_currency('SOS', '706', 'Somali Shilling', ['SOMALIA'])
add_currency('MZN', '943', 'Metical', ['MOZAMBIQUE'])
add_currency('XFU', 'Nil', 'UIC-Franc', [])
add_currency('NOK', '578', 'Norwegian Krone', ['BOUVET ISLAND', 'NORWAY', 'SVALBARD AND JAN MAYEN'])
add_currency('ISK', '352', 'Iceland Krona', ['ICELAND'])
add_currency('GEL', '981', 'Lari', ['GEORGIA'])
add_currency('ILS', '376', 'New Israeli Sheqel', ['ISRAEL'])
add_currency('HUF', '348', 'Forint', ['HUNGARY'])
add_currency('UAH', '980', 'Hryvnia', ['UKRAINE'])
add_currency('RUB', '643', 'Russian Ruble', ['RUSSIAN FEDERATION'])
add_currency('IRR', '364', 'Iranian Rial', ['IRAN'])
add_currency('BMD', '060', 'Bermudian Dollar (customarily known as Bermuda Dollar)', ['BERMUDA'])
add_currency('MGA', '969', 'Malagasy Ariary', ['MADAGASCAR'])
add_currency('MVR', '462', 'Rufiyaa', ['MALDIVES'])
add_currency('QAR', '634', 'Qatari Rial', ['QATAR'])
add_currency('VND', '704', 'Dong', ['VIET NAM'])
add_currency('MRO', '478', 'Ouguiya', ['MAURITANIA'])
add_currency('NPR', '524', 'Nepalese Rupee', ['NEPAL'])
add_currency('TZS', '834', 'Tanzanian Shilling', ['TANZANIA'])
add_currency('BIF', '108', 'Burundi Franc', ['BURUNDI'])
add_currency('XPT', '962', 'Platinum', [])
add_currency('KHR', '116', 'Riel', ['CAMBODIA'])
add_currency('SYP', '760', 'Syrian Pound', ['SYRIAN ARAB REPUBLIC'])
add_currency('BHD', '048', 'Bahraini Dinar', ['BAHRAIN'])
add_currency('XDR', '960', 'SDR', ['INTERNATIONAL MONETARY FUND (I.M.F)'])
add_currency('STD', '678', 'Dobra', ['SAO TOME AND PRINCIPE'])
add_currency('BAM', '977', 'Convertible Marks', ['BOSNIA AND HERZEGOVINA'])
add_currency('LTL', '440', 'Lithuanian Litas', ['LITHUANIA'])
add_currency('ETB', '230', 'Ethiopian Birr', ['ETHIOPIA'])
add_currency('XPF', '953', 'CFP Franc', ['FRENCH POLYNESIA', 'NEW CALEDONIA', 'WALLIS AND FUTUNA'])

add_currency('XYZ', '999', 'Default currency.', [])

DEFAULT_CURRENCY = get_currency(DEFAULT_CURRENCY_CODE)