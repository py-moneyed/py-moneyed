# -*- coding: utf-8 -*-

from decimal import Decimal
import locale

# NOTE: this sets the default locale to the local environment's (and
# something other than the useless 'C' locale), but possibly it should
# be set/changed depending on the Currency country.  However that will
# require a lookup: given the currency code, return the locale code;
# the pycountry package may provide a way to do that.  Revisit this
# later.  KW 1/2011.
DEFAULT_LOCALE = (
    "%s.%s"
    % (locale.getdefaultlocale()[0],
       locale.getdefaultlocale()[1].lower()))
locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)


class Currency(object):
    """
    A Currency represents a form of money issued by governments, and
    used in one or more states/countries.  A Currency instance
    encapsulates the related data of: the ISO currency/numeric code, a
    canonical name, countries the currency is used in, and an exchange
    rate - the last remains unimplemented however.
    """

    code = 'XYZ'
    country = ''
    countries = []
    name = ''
    numeric = '999'
    exchange_rate = Decimal('1.0')

    def __init__(self, code='', numeric='999', name='', countries=[]):
        self.code = code
        self.countries = countries
        self.name = name
        self.numeric = numeric

    def __repr__(self):
        return self.code

    def set_exchange_rate(self, rate):
        # This method could later use a web-lookup of the current
        # exchange rate; currently it's just a manual field
        # setting. 7/2010
        if not isinstance(rate, Decimal):
            rate = Decimal(str(rate))
        self.exchange_rate = rate


# With Currency class defined, setup some needed module globals:
CURRENCIES = {}
CURRENCIES['XYZ'] = Currency(code='XYZ', numeric='999')
DEFAULT_CURRENCY = CURRENCIES['XYZ']


def set_default_currency(code='XYZ'):
    global DEFAULT_CURRENCY
    DEFAULT_CURRENCY = CURRENCIES[code]


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


class Money(object):
    """
    A Money instance is a combination of data - an amount and a
    currency - along with operators that handle the semantics of money
    operations in a better way than just dealing with raw Decimal or
    ($DEITY forbid) floats.
    """

    amount = Decimal('0.0')
    currency = DEFAULT_CURRENCY

    def __init__(self, amount=Decimal('0.0'), currency=None):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        self.amount = amount
        if not currency:
            self.currency = DEFAULT_CURRENCY
        else:
            if not isinstance(currency, Currency):
                currency = CURRENCIES[str(currency).upper()]
            self.currency = currency

    def __unicode__(self):
        return "%s %s" % (
            locale.currency(self.amount, grouping=True),
            self.currency)

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
                currency=DEFAULT_CURRENCY)

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

    def convert_to_default(self):
        return Money(
            amount=(self.amount * self.currency.exchange_rate),
            currency=DEFAULT_CURRENCY)

    def convert_to(self, currency):
        """
        Convert from one currency to another.
        """
        return None  # TODO

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

CURRENCIES['BZD'] = Currency(code='BZD', numeric='084', name='Belize Dollar', countries=['BELIZE'])
CURRENCIES['YER'] = Currency(code='YER', numeric='886', name='Yemeni Rial', countries=['YEMEN'])
CURRENCIES['XBA'] = Currency(code='XBA', numeric='955', name='Bond Markets Units European Composite Unit (EURCO)', countries=[])
CURRENCIES['SLL'] = Currency(code='SLL', numeric='694', name='Leone', countries=['SIERRA LEONE'])
CURRENCIES['ERN'] = Currency(code='ERN', numeric='232', name='Nakfa', countries=['ERITREA'])
CURRENCIES['NGN'] = Currency(code='NGN', numeric='566', name='Naira', countries=['NIGERIA'])
CURRENCIES['CRC'] = Currency(code='CRC', numeric='188', name='Costa Rican Colon', countries=['COSTA RICA'])
CURRENCIES['VEF'] = Currency(code='VEF', numeric='937', name='Bolivar Fuerte', countries=['VENEZUELA'])
CURRENCIES['LAK'] = Currency(code='LAK', numeric='418', name='Kip', countries=['LAO PEOPLES DEMOCRATIC REPUBLIC'])
CURRENCIES['DZD'] = Currency(code='DZD', numeric='012', name='Algerian Dinar', countries=['ALGERIA'])
CURRENCIES['SZL'] = Currency(code='SZL', numeric='748', name='Lilangeni', countries=['SWAZILAND'])
CURRENCIES['MOP'] = Currency(code='MOP', numeric='446', name='Pataca', countries=['MACAO'])
CURRENCIES['BYR'] = Currency(code='BYR', numeric='974', name='Belarussian Ruble', countries=['BELARUS'])
CURRENCIES['MUR'] = Currency(code='MUR', numeric='480', name='Mauritius Rupee', countries=['MAURITIUS'])
CURRENCIES['WST'] = Currency(code='WST', numeric='882', name='Tala', countries=['SAMOA'])
CURRENCIES['LRD'] = Currency(code='LRD', numeric='430', name='Liberian Dollar', countries=['LIBERIA'])
CURRENCIES['MMK'] = Currency(code='MMK', numeric='104', name='Kyat', countries=['MYANMAR'])
CURRENCIES['KGS'] = Currency(code='KGS', numeric='417', name='Som', countries=['KYRGYZSTAN'])
CURRENCIES['PYG'] = Currency(code='PYG', numeric='600', name='Guarani', countries=['PARAGUAY'])
CURRENCIES['IDR'] = Currency(code='IDR', numeric='360', name='Rupiah', countries=['INDONESIA'])
CURRENCIES['XBD'] = Currency(code='XBD', numeric='958', name='European Unit of Account 17(E.U.A.-17)', countries=[])
CURRENCIES['GTQ'] = Currency(code='GTQ', numeric='320', name='Quetzal', countries=['GUATEMALA'])
CURRENCIES['CAD'] = Currency(code='CAD', numeric='124', name='Canadian Dollar', countries=['CANADA'])
CURRENCIES['AWG'] = Currency(code='AWG', numeric='533', name='Aruban Guilder', countries=['ARUBA'])
CURRENCIES['TTD'] = Currency(code='TTD', numeric='780', name='Trinidad and Tobago Dollar', countries=['TRINIDAD AND TOBAGO'])
CURRENCIES['PKR'] = Currency(code='PKR', numeric='586', name='Pakistan Rupee', countries=['PAKISTAN'])
CURRENCIES['XBC'] = Currency(code='XBC', numeric='957', name='European Unit of Account 9(E.U.A.-9)', countries=[])
CURRENCIES['UZS'] = Currency(code='UZS', numeric='860', name='Uzbekistan Sum', countries=['UZBEKISTAN'])
CURRENCIES['XCD'] = Currency(code='XCD', numeric='951', name='East Caribbean Dollar', countries=['ANGUILLA', 'ANTIGUA AND BARBUDA', 'DOMINICA', 'GRENADA', 'MONTSERRAT', 'SAINT KITTS AND NEVIS', 'SAINT LUCIA', 'SAINT VINCENT AND THE GRENADINES'])
CURRENCIES['VUV'] = Currency(code='VUV', numeric='548', name='Vatu', countries=['VANUATU'])
CURRENCIES['KMF'] = Currency(code='KMF', numeric='174', name='Comoro Franc', countries=['COMOROS'])
CURRENCIES['AZN'] = Currency(code='AZN', numeric='944', name='Azerbaijanian Manat', countries=['AZERBAIJAN'])
CURRENCIES['XPD'] = Currency(code='XPD', numeric='964', name='Palladium', countries=[])
CURRENCIES['MNT'] = Currency(code='MNT', numeric='496', name='Tugrik', countries=['MONGOLIA'])
CURRENCIES['ANG'] = Currency(code='ANG', numeric='532', name='Netherlands Antillian Guilder', countries=['NETHERLANDS ANTILLES'])
CURRENCIES['LBP'] = Currency(code='LBP', numeric='422', name='Lebanese Pound', countries=['LEBANON'])
CURRENCIES['KES'] = Currency(code='KES', numeric='404', name='Kenyan Shilling', countries=['KENYA'])
CURRENCIES['GBP'] = Currency(code='GBP', numeric='826', name='Pound Sterling', countries=['UNITED KINGDOM'])
CURRENCIES['SEK'] = Currency(code='SEK', numeric='752', name='Swedish Krona', countries=['SWEDEN'])
CURRENCIES['AFN'] = Currency(code='AFN', numeric='971', name='Afghani', countries=['AFGHANISTAN'])
CURRENCIES['KZT'] = Currency(code='KZT', numeric='398', name='Tenge', countries=['KAZAKHSTAN'])
CURRENCIES['ZMK'] = Currency(code='ZMK', numeric='894', name='Kwacha', countries=['ZAMBIA'])
CURRENCIES['SKK'] = Currency(code='SKK', numeric='703', name='Slovak Koruna', countries=['SLOVAKIA'])
CURRENCIES['DKK'] = Currency(code='DKK', numeric='208', name='Danish Krone', countries=['DENMARK', 'FAROE ISLANDS', 'GREENLAND'])
CURRENCIES['TMM'] = Currency(code='TMM', numeric='795', name='Manat', countries=['TURKMENISTAN'])
CURRENCIES['AMD'] = Currency(code='AMD', numeric='051', name='Armenian Dram', countries=['ARMENIA'])
CURRENCIES['SCR'] = Currency(code='SCR', numeric='690', name='Seychelles Rupee', countries=['SEYCHELLES'])
CURRENCIES['FJD'] = Currency(code='FJD', numeric='242', name='Fiji Dollar', countries=['FIJI'])
CURRENCIES['SHP'] = Currency(code='SHP', numeric='654', name='Saint Helena Pound', countries=['SAINT HELENA'])
CURRENCIES['ALL'] = Currency(code='ALL', numeric='008', name='Lek', countries=['ALBANIA'])
CURRENCIES['TOP'] = Currency(code='TOP', numeric='776', name='Paanga', countries=['TONGA'])
CURRENCIES['UGX'] = Currency(code='UGX', numeric='800', name='Uganda Shilling', countries=['UGANDA'])
CURRENCIES['OMR'] = Currency(code='OMR', numeric='512', name='Rial Omani', countries=['OMAN'])
CURRENCIES['DJF'] = Currency(code='DJF', numeric='262', name='Djibouti Franc', countries=['DJIBOUTI'])
CURRENCIES['BND'] = Currency(code='BND', numeric='096', name='Brunei Dollar', countries=['BRUNEI DARUSSALAM'])
CURRENCIES['TND'] = Currency(code='TND', numeric='788', name='Tunisian Dinar', countries=['TUNISIA'])
CURRENCIES['SBD'] = Currency(code='SBD', numeric='090', name='Solomon Islands Dollar', countries=['SOLOMON ISLANDS'])
CURRENCIES['GHS'] = Currency(code='GHS', numeric='936', name='Ghana Cedi', countries=['GHANA'])
CURRENCIES['GNF'] = Currency(code='GNF', numeric='324', name='Guinea Franc', countries=['GUINEA'])
CURRENCIES['CVE'] = Currency(code='CVE', numeric='132', name='Cape Verde Escudo', countries=['CAPE VERDE'])
CURRENCIES['ARS'] = Currency(code='ARS', numeric='032', name='Argentine Peso', countries=['ARGENTINA'])
CURRENCIES['GMD'] = Currency(code='GMD', numeric='270', name='Dalasi', countries=['GAMBIA'])
CURRENCIES['ZWD'] = Currency(code='ZWD', numeric='716', name='Zimbabwe Dollar', countries=['ZIMBABWE'])
CURRENCIES['MWK'] = Currency(code='MWK', numeric='454', name='Kwacha', countries=['MALAWI'])
CURRENCIES['BDT'] = Currency(code='BDT', numeric='050', name='Taka', countries=['BANGLADESH'])
CURRENCIES['KWD'] = Currency(code='KWD', numeric='414', name='Kuwaiti Dinar', countries=['KUWAIT'])
CURRENCIES['EUR'] = Currency(code='EUR', numeric='978', name='Euro', countries=['ANDORRA', 'AUSTRIA', 'BELGIUM', 'FINLAND', 'FRANCE', 'FRENCH GUIANA', 'FRENCH SOUTHERN TERRITORIES', 'GERMANY', 'GREECE', 'GUADELOUPE', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'MARTINIQUE', 'MAYOTTE', 'MONACO', 'MONTENEGRO', 'NETHERLANDS', 'PORTUGAL', 'R.UNION', 'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SLOVENIA', 'SPAIN'])
CURRENCIES['CHF'] = Currency(code='CHF', numeric='756', name='Swiss Franc', countries=['LIECHTENSTEIN'])
CURRENCIES['XAG'] = Currency(code='XAG', numeric='961', name='Silver', countries=[])
CURRENCIES['SRD'] = Currency(code='SRD', numeric='968', name='Surinam Dollar', countries=['SURINAME'])
CURRENCIES['DOP'] = Currency(code='DOP', numeric='214', name='Dominican Peso', countries=['DOMINICAN REPUBLIC'])
CURRENCIES['PEN'] = Currency(code='PEN', numeric='604', name='Nuevo Sol', countries=['PERU'])
CURRENCIES['KPW'] = Currency(code='KPW', numeric='408', name='North Korean Won', countries=['KOREA'])
CURRENCIES['SGD'] = Currency(code='SGD', numeric='702', name='Singapore Dollar', countries=['SINGAPORE'])
CURRENCIES['TWD'] = Currency(code='TWD', numeric='901', name='New Taiwan Dollar', countries=['TAIWAN'])
CURRENCIES['USD'] = Currency(code='USD', numeric='840', name='US Dollar', countries=['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY', 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA', 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO', 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES MINOR OUTLYING ISLANDS', 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
CURRENCIES['BGN'] = Currency(code='BGN', numeric='975', name='Bulgarian Lev', countries=['BULGARIA'])
CURRENCIES['MAD'] = Currency(code='MAD', numeric='504', name='Moroccan Dirham', countries=['MOROCCO', 'WESTERN SAHARA'])
CURRENCIES['XYZ'] = Currency(code='XYZ', numeric='999', name='The codes assigned for transactions where no currency is involved are:', countries=[])
CURRENCIES['SAR'] = Currency(code='SAR', numeric='682', name='Saudi Riyal', countries=['SAUDI ARABIA'])
CURRENCIES['AUD'] = Currency(code='AUD', numeric='036', name='Australian Dollar', countries=['AUSTRALIA', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'HEARD ISLAND AND MCDONALD ISLANDS', 'KIRIBATI', 'NAURU', 'NORFOLK ISLAND', 'TUVALU'])
CURRENCIES['KYD'] = Currency(code='KYD', numeric='136', name='Cayman Islands Dollar', countries=['CAYMAN ISLANDS'])
CURRENCIES['KRW'] = Currency(code='KRW', numeric='410', name='Won', countries=['KOREA'])
CURRENCIES['GIP'] = Currency(code='GIP', numeric='292', name='Gibraltar Pound', countries=['GIBRALTAR'])
CURRENCIES['TRY'] = Currency(code='TRY', numeric='949', name='New Turkish Lira', countries=['TURKEY'])
CURRENCIES['XAU'] = Currency(code='XAU', numeric='959', name='Gold', countries=[])
CURRENCIES['CZK'] = Currency(code='CZK', numeric='203', name='Czech Koruna', countries=['CZECH REPUBLIC'])
CURRENCIES['JMD'] = Currency(code='JMD', numeric='388', name='Jamaican Dollar', countries=['JAMAICA'])
CURRENCIES['BSD'] = Currency(code='BSD', numeric='044', name='Bahamian Dollar', countries=['BAHAMAS'])
CURRENCIES['BWP'] = Currency(code='BWP', numeric='072', name='Pula', countries=['BOTSWANA'])
CURRENCIES['GYD'] = Currency(code='GYD', numeric='328', name='Guyana Dollar', countries=['GUYANA'])
CURRENCIES['XTS'] = Currency(code='XTS', numeric='963', name='Codes specifically reserved for testing purposes', countries=[])
CURRENCIES['LYD'] = Currency(code='LYD', numeric='434', name='Libyan Dinar', countries=['LIBYAN ARAB JAMAHIRIYA'])
CURRENCIES['EGP'] = Currency(code='EGP', numeric='818', name='Egyptian Pound', countries=['EGYPT'])
CURRENCIES['THB'] = Currency(code='THB', numeric='764', name='Baht', countries=['THAILAND'])
CURRENCIES['MKD'] = Currency(code='MKD', numeric='807', name='Denar', countries=['MACEDONIA'])
CURRENCIES['SDG'] = Currency(code='SDG', numeric='938', name='Sudanese Pound', countries=['SUDAN'])
CURRENCIES['AED'] = Currency(code='AED', numeric='784', name='UAE Dirham', countries=['UNITED ARAB EMIRATES'])
CURRENCIES['JOD'] = Currency(code='JOD', numeric='400', name='Jordanian Dinar', countries=['JORDAN'])
CURRENCIES['JPY'] = Currency(code='JPY', numeric='392', name='Yen', countries=['JAPAN'])
CURRENCIES['ZAR'] = Currency(code='ZAR', numeric='710', name='Rand', countries=['SOUTH AFRICA'])
CURRENCIES['HRK'] = Currency(code='HRK', numeric='191', name='Croatian Kuna', countries=['CROATIA'])
CURRENCIES['AOA'] = Currency(code='AOA', numeric='973', name='Kwanza', countries=['ANGOLA'])
CURRENCIES['RWF'] = Currency(code='RWF', numeric='646', name='Rwanda Franc', countries=['RWANDA'])
CURRENCIES['CUP'] = Currency(code='CUP', numeric='192', name='Cuban Peso', countries=['CUBA'])
CURRENCIES['XFO'] = Currency(code='XFO', numeric='Nil', name='Gold-Franc', countries=[])
CURRENCIES['BBD'] = Currency(code='BBD', numeric='052', name='Barbados Dollar', countries=['BARBADOS'])
CURRENCIES['PGK'] = Currency(code='PGK', numeric='598', name='Kina', countries=['PAPUA NEW GUINEA'])
CURRENCIES['LKR'] = Currency(code='LKR', numeric='144', name='Sri Lanka Rupee', countries=['SRI LANKA'])
CURRENCIES['RON'] = Currency(code='RON', numeric='946', name='New Leu', countries=['ROMANIA'])
CURRENCIES['PLN'] = Currency(code='PLN', numeric='985', name='Zloty', countries=['POLAND'])
CURRENCIES['IQD'] = Currency(code='IQD', numeric='368', name='Iraqi Dinar', countries=['IRAQ'])
CURRENCIES['TJS'] = Currency(code='TJS', numeric='972', name='Somoni', countries=['TAJIKISTAN'])
CURRENCIES['MDL'] = Currency(code='MDL', numeric='498', name='Moldovan Leu', countries=['MOLDOVA'])
CURRENCIES['MYR'] = Currency(code='MYR', numeric='458', name='Malaysian Ringgit', countries=['MALAYSIA'])
CURRENCIES['CNY'] = Currency(code='CNY', numeric='156', name='Yuan Renminbi', countries=['CHINA'])
CURRENCIES['LVL'] = Currency(code='LVL', numeric='428', name='Latvian Lats', countries=['LATVIA'])
CURRENCIES['INR'] = Currency(code='INR', numeric='356', name='Indian Rupee', countries=['INDIA'])
CURRENCIES['FKP'] = Currency(code='FKP', numeric='238', name='Falkland Islands Pound', countries=['FALKLAND ISLANDS (MALVINAS)'])
CURRENCIES['NIO'] = Currency(code='NIO', numeric='558', name='Cordoba Oro', countries=['NICARAGUA'])
CURRENCIES['PHP'] = Currency(code='PHP', numeric='608', name='Philippine Peso', countries=['PHILIPPINES'])
CURRENCIES['HNL'] = Currency(code='HNL', numeric='340', name='Lempira', countries=['HONDURAS'])
CURRENCIES['HKD'] = Currency(code='HKD', numeric='344', name='Hong Kong Dollar', countries=['HONG KONG'])
CURRENCIES['NZD'] = Currency(code='NZD', numeric='554', name='New Zealand Dollar', countries=['COOK ISLANDS', 'NEW ZEALAND', 'NIUE', 'PITCAIRN', 'TOKELAU'])
CURRENCIES['BRL'] = Currency(code='BRL', numeric='986', name='Brazilian Real', countries=['BRAZIL'])
CURRENCIES['RSD'] = Currency(code='RSD', numeric='941', name='Serbian Dinar', countries=['SERBIA'])
CURRENCIES['XBB'] = Currency(code='XBB', numeric='956', name='European Monetary Unit (E.M.U.-6)', countries=[])
CURRENCIES['EEK'] = Currency(code='EEK', numeric='233', name='Kroon', countries=['ESTONIA'])
CURRENCIES['SOS'] = Currency(code='SOS', numeric='706', name='Somali Shilling', countries=['SOMALIA'])
CURRENCIES['MZN'] = Currency(code='MZN', numeric='943', name='Metical', countries=['MOZAMBIQUE'])
CURRENCIES['XFU'] = Currency(code='XFU', numeric='Nil', name='UIC-Franc', countries=[])
CURRENCIES['NOK'] = Currency(code='NOK', numeric='578', name='Norwegian Krone', countries=['BOUVET ISLAND', 'NORWAY', 'SVALBARD AND JAN MAYEN'])
CURRENCIES['ISK'] = Currency(code='ISK', numeric='352', name='Iceland Krona', countries=['ICELAND'])
CURRENCIES['GEL'] = Currency(code='GEL', numeric='981', name='Lari', countries=['GEORGIA'])
CURRENCIES['ILS'] = Currency(code='ILS', numeric='376', name='New Israeli Sheqel', countries=['ISRAEL'])
CURRENCIES['HUF'] = Currency(code='HUF', numeric='348', name='Forint', countries=['HUNGARY'])
CURRENCIES['UAH'] = Currency(code='UAH', numeric='980', name='Hryvnia', countries=['UKRAINE'])
CURRENCIES['RUB'] = Currency(code='RUB', numeric='643', name='Russian Ruble', countries=['RUSSIAN FEDERATION'])
CURRENCIES['IRR'] = Currency(code='IRR', numeric='364', name='Iranian Rial', countries=['IRAN'])
CURRENCIES['BMD'] = Currency(code='BMD', numeric='060', name='Bermudian Dollar (customarily known as Bermuda Dollar)', countries=['BERMUDA'])
CURRENCIES['MGA'] = Currency(code='MGA', numeric='969', name='Malagasy Ariary', countries=['MADAGASCAR'])
CURRENCIES['MVR'] = Currency(code='MVR', numeric='462', name='Rufiyaa', countries=['MALDIVES'])
CURRENCIES['QAR'] = Currency(code='QAR', numeric='634', name='Qatari Rial', countries=['QATAR'])
CURRENCIES['VND'] = Currency(code='VND', numeric='704', name='Dong', countries=['VIET NAM'])
CURRENCIES['MRO'] = Currency(code='MRO', numeric='478', name='Ouguiya', countries=['MAURITANIA'])
CURRENCIES['NPR'] = Currency(code='NPR', numeric='524', name='Nepalese Rupee', countries=['NEPAL'])
CURRENCIES['TZS'] = Currency(code='TZS', numeric='834', name='Tanzanian Shilling', countries=['TANZANIA'])
CURRENCIES['BIF'] = Currency(code='BIF', numeric='108', name='Burundi Franc', countries=['BURUNDI'])
CURRENCIES['XPT'] = Currency(code='XPT', numeric='962', name='Platinum', countries=[])
CURRENCIES['KHR'] = Currency(code='KHR', numeric='116', name='Riel', countries=['CAMBODIA'])
CURRENCIES['SYP'] = Currency(code='SYP', numeric='760', name='Syrian Pound', countries=['SYRIAN ARAB REPUBLIC'])
CURRENCIES['BHD'] = Currency(code='BHD', numeric='048', name='Bahraini Dinar', countries=['BAHRAIN'])
CURRENCIES['XDR'] = Currency(code='XDR', numeric='960', name='SDR', countries=['INTERNATIONAL MONETARY FUND (I.M.F)'])
CURRENCIES['STD'] = Currency(code='STD', numeric='678', name='Dobra', countries=['SAO TOME AND PRINCIPE'])
CURRENCIES['BAM'] = Currency(code='BAM', numeric='977', name='Convertible Marks', countries=['BOSNIA AND HERZEGOVINA'])
CURRENCIES['LTL'] = Currency(code='LTL', numeric='440', name='Lithuanian Litas', countries=['LITHUANIA'])
CURRENCIES['ETB'] = Currency(code='ETB', numeric='230', name='Ethiopian Birr', countries=['ETHIOPIA'])
CURRENCIES['XPF'] = Currency(code='XPF', numeric='953', name='CFP Franc', countries=['FRENCH POLYNESIA', 'NEW CALEDONIA', 'WALLIS AND FUTUNA'])
