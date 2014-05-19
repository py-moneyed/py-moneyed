# -*- coding: utf-8 -*-

from decimal import Decimal
import copy

from json import dumps

DEFAULT_CURRENCY_CODE = 'BTC'

class Currency(object):
    """
    A Currency represents a form of money issued by governments, and
    used in one or more states/countries.  A Currency instance
    encapsulates the related data of: the ISO currency/numeric code, a
    canonical name, countries the currency is used in, and an exchange
    rate - the last remains unimplemented however.
    """

    def __init__(self, code='', numeric='999', name='', countries=[], significantDigits=8):
        self.code = code
        self.countries = countries
        self.name = name
        self.numeric = numeric
        self.significantDigits = significantDigits
        self.quantizer = Decimal(10) ** (Decimal(-1) * significantDigits)

    def __repr__(self):
        return self.code

    def __eq__(self, other):
        if isinstance(other, Currency):
            return self.code == other.code
        elif isinstance(other, str):
            return self.code == other
        else:
            return False

    def __ne__(self, other):
        result = self.__eq__(other)
        return not result

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
            u"No currency with code %s is defined." % code)


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

    def __dict__(self):
        return {'a': self.amount, 'c': self.currency}

    def __getstate__(self):
        return {'a': self.amount, 'c': str(self.currency)}

    def __setstate__(self, data):
        self.__init__(data["a"], data["c"])

    def __repr__(self):
        return u"%s %s" % (self.amount.normalize(), self.currency)

    def __unicode__(self):
        from moneyed.localization import format_money
        return format_money(self)

    def __str__(self):
        from moneyed.localization import format_money
        return format_money(self)

    def __copy__(self):
        return Money(amount=str(self.amount), currency=str(self.currency))

    def prep_json(self):
        return {u'a':unicode(self.amount), u'c': unicode(self.currency)}

    def to_json(self):
        return dumps(self.prep_json())

    def __pos__(self):
        return Money(
            amount=self.amount,
            currency=self.currency)

    def __neg__(self):
        return Money(
            amount=-self.amount,
            currency=self.currency)

    def __add__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return Money(
                    amount=self.amount + other.amount,
                    currency=self.currency)
        elif isinstance(other, Decimal):
            return Money(amount=self.amount + other, currency=self.currency)
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            return Money(amount=self.amount + Decimal(str(other)), currency=self.currency)
        raise TypeError('Cannot add or subtract a ' +
                        'Money and non-number instance.')

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return Money(
                    amount=(self.amount * other.amount).quantize(self.currency.quantizer).normalize(),
                    currency=self.currency)
            else:
                raise MoneyComparisonError(other)
        elif isinstance(other, Decimal):
            return Money(
                amount=(self.amount * other).quantize(self.currency.quantizer).normalize(),
                currency=self.currency)
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            return Money(
                amount=(self.amount * Decimal(str(other))).quantize(self.currency.quantizer).normalize(),
                currency=self.currency)
        raise TypeError('Cannot multiply two non-number instances.')

    def __div__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return Money(
                    amount=(self.amount / other.amount).quantize(self.currency.quantizer).normalize(),
                    currency=self.currency)
            else:
                raise MoneyComparisonError(other)
        elif isinstance(other, Decimal):
            return Money(
                amount=(self.amount / other).quantize(self.currency.quantizer).normalize(),
                currency=self.currency)
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            return Money(
                amount=(self.amount / Decimal(str(other))).quantize(self.currency.quantizer).normalize(),
                currency=self.currency)
        raise TypeError('Cannot multiply two non-number instances.')


    def __abs__(self):
        return Money(
            amount=abs(self.amount),
            currency=self.currency
        )

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
        if isinstance(other, Money):
            return self.amount == other.amount \
                   and (self.currency == other.currency)
        elif isinstance(other, Decimal):
            return self.amount == other
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            return self.amount == Decimal(str(other))
        else:
            return False

    def __ne__(self, other):
        result = self.__eq__(other)
        return not result

    def __lt__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return self.amount < other.amount
            else:
                raise MoneyComparisonError(other)
        elif isinstance(other, Decimal):
            return self.amount < other
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            return self.amount < Decimal(str(other))
        else:
            raise MoneyComparisonError(other)

    def __gt__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return self.amount > other.amount
            else:
                raise MoneyComparisonError(other)
        elif isinstance(other, Decimal):
            return self.amount > other
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            return self.amount > Decimal(str(other))
        else:
            raise MoneyComparisonError(other)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other


class MultiMoney(object):
    """
    A MultiMoney is a dict that may contain multiple Money objects of different currencies.
    This is mainly used for performing address accounting, but can also be applied to conversions
    with a little tweaking.
    """
    moneys = {}

    def __init__(self, *args):
        self.moneys = {}
        for mon in args:
            if isinstance(mon, Money):
                self.addMoney(mon)

    def __dict__(self):
        return copy.copy(self).moneys

    def __getstate__(self):
        psd = {}
        for money in copy.copy(self).getMoneys():
            psd[str(money.currency)] = Money.__getstate__(money)
        return psd

    def __setstate__(self, data):
        l = []
        for m, mon in data.iteritems():
            l.append(Money(mon["a"], mon["c"]))
        return self.__init__(*l)

    def __copy__(self):
        newSelf = MultiMoney()
        for money in self.getMoneys():
            newSelf += copy.copy(money)
        return newSelf

    def prep_json(self):
        encMoney = {u'mm':True}
        tself = copy.copy(self)
        for mon in tself.getMoneys():
            encMoney[unicode(mon.currency)] = mon.prep_json()
        return encMoney

    def to_json(self):
        return dumps(self.prep_json())

    def isEmpty(self):
        for mon in self.getMoneys():
            if mon > 0:
                return False
        return True

    def addMoney(self, mon):
        if self.hasCurrency(str(mon.currency)):
            self.moneys[str(mon.currency)] += mon
        else:
            self.moneys[str(mon.currency)] = mon

    def hasCurrency(self, currency):
        return currency in self.moneys

    def getCurrencies(self):
        currencies = []
        for money in self.moneys:
            currencies.append(str(self.moneys[money].currency))
        if len(currencies) == 0:
            return ['BTC']
        return currencies

    def getMoneys(self, currency=None):
        if currency is not None:
            currency = str(currency)
            if not self.hasCurrency(currency):
                self.addMoney(Money(currency=currency))
            return self.moneys[currency]
        return self.moneys.itervalues()

    def __repr__(self):
        rep = u""
        first = True
        for mon in self.getMoneys():
            if first:
                str = u"%s %s" % (mon.amount.normalize(), mon.currency.code)
                first = False
            else:
                str = u", %s %s" % (mon.amount.normalize(), mon.currency.code)
            rep = rep + str
        return rep

    def __unicode__(self):
        from moneyed.localization import format_money
        first = True
        us = u""
        for mon in self.getMoneys():
            if first:
                us = u"" + format_money(mon)
                first = False
            else:
                us += u", " + format_money(mon)
        return us

    def __str__(self):
        from moneyed.localization import format_money
        first = True
        us = u""
        for mon in self.getMoneys():
            if first:
                us = u"" + format_money(mon)
                first = False
            else:
                us = us + u", " + format_money(mon)
        return us

    def __pos__(self):
        moneys = []
        for mon in self.getMoneys():
            moneys.append(Money(amount=mon.amount,
                                currency=mon.currency))
        return MultiMoney(*moneys)

    def __neg__(self):
        moneys = []
        for mon in self.getMoneys():
            moneys.append(Money(amount=-mon.amount,
                                currency=mon.currency))
        return MultiMoney(*moneys)

    def __add__(self, other):
        copySelf = self.__copy__()
        if isinstance(other, MultiMoney):
            for mon in other.getMoneys():
                copySelf.addMoney(mon)
        elif isinstance(other, Money):
            copySelf.addMoney(other)
        else:
            raise TypeError('Cannot add or subtract a ' +
                            'MultiMoney and non-Money, non-MultiMoney instance.')
        return copySelf

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        copySelf = self.__pos__()
        if isinstance(other, MultiMoney):
            for mon in other.getMoneys():
                if copySelf.hasCurrency(mon.currency.code):
                    copySelf.moneys[mon.currency.code] *= mon
                else:
                    copySelf.moneys[mon.currency.code] = Money(amount=0, currency=mon.currency.code)
            for mon in copySelf:
                if not other.hasCurrency(mon.currency.code):
                    copySelf.moneys[mon.currency.code] = Money(amount=0, currency=mon.currency.code)
            return copySelf
        elif isinstance(other, Money):
            if copySelf.hasCurrency(other.currency.code):
                copySelf.moneys[other.currency.code] *= other
            else:
                copySelf.moneys[other.currency.code] = Money(amount=0, currency=other.currency.code)
            return copySelf
        elif isinstance(other, Decimal) or isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            for mon in self.getMoneys():
                copySelf.moneys[mon.currency.code] = mon * other
            return copySelf
        raise TypeError('Cannot multiply two non-number instances.')

    def __div__(self, other):
        copySelf = self.__pos__()
        if isinstance(other, MultiMoney):
            for mon in other.getMoneys():
                if copySelf.hasCurrency(mon.currency.code):
                    copySelf.moneys[mon.currency.code] /= mon
                else:
                    copySelf.moneys[mon.currency.code] = Money(amount=0, currency=mon.currency.code)
            for mon in copySelf.moneys:
                if not other.hasCurrency(mon.currency.code):
                    copySelf.moneys[mon.currency.code] = Money(amount=0, currency=mon.currency.code)
            return copySelf
        elif isinstance(other, Money):
            if copySelf.hasCurrency(other.currency.code):
                copySelf.moneys[other.currency.code] /= other
            else:
                copySelf.moneys[other.currency.code] = Money(amount=0, currency=other.currency.code)
            return copySelf
        elif isinstance(other, Decimal) or isinstance(other, float) or isinstance(other, int) or isinstance(other, str):
            for mon in self.getMoneys():
                copySelf.moneys[mon.currency.code] = mon / other
            return copySelf
        raise TypeError('Cannot multiply two non-number instances.')

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rdiv__ = __div__

    # _______________________________________
    # Override comparison operators
    def __eq__(self, other):
        if isinstance(other, MultiMoney):
            for mon in other.getMoneys():
                if not self.hasCurrency(str(mon.currency)):
                    if mon == 0:
                        continue
                    else:
                        return False
                else:
                    if not mon == self.getMoneys(str(mon.currency)):
                        return False
            for mon in self.getMoneys():
                if not other.hasCurrency(mon.currency.code):
                    if mon == 0:
                        continue
                    else:
                        return False
                else:
                    if not mon == other.getMoneys(str(mon.currency)):
                        return False
        elif isinstance(other, Money):
            return self.__eq__(MultiMoney(other))
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, Decimal):
            return self.__eq__(MultiMoney(Money(other)))
        else:
            raise TypeError("Cannot compare MultiMoney to non-MultiMoney")
        return True

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        # Assume any currency not present has a 0 amount.
        if isinstance(other, MultiMoney):
            if self == other:
                return False
            for mon in other.getMoneys():
                if self.hasCurrency(mon.currency.code):
                    if self.getMoneys(mon.currency.code) > mon:
                        return False
                elif mon < 0:
                    return False
            for mon in self.getMoneys():
                if not other.hasCurrency(str(mon.currency)) and mon > 0:
                    return False
            return True
        elif isinstance(other, Money):
            if self.hasCurrency(other.currency.code):
                return self.moneys[other.currency.code] < other
            elif other < 0:
                return False
            return True
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, Decimal):
            for money in self.getMoneys():
                if money.amount >= Decimal(str(other)):
                    return False
            return True
        else:
            raise TypeError("Cannot compare MultiMoney to non-MultiMoney")

    def __gt__(self, other):
        if isinstance(other, MultiMoney):
            if self == other:
                return False
            for mon in other.getMoneys():
                if self.hasCurrency(mon.currency.code):
                    if self.moneys[mon.currency.code] < mon:
                        return False
                elif mon > 0:
                    return False
            return True
        elif isinstance(other, Money):
            if self.hasCurrency(other.currency.code):
                return self.moneys[other.currency.code] > other
            elif other > 0:
                return False
            return True
        elif isinstance(other, float) or isinstance(other, int) or isinstance(other, Decimal):
            for money in self.getMoneys():
                if money.amount <= Decimal(str(other)):
                    return False
            return True
        else:
            raise TypeError("Cannot compare MultiMoney to non-MultiMoney")

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

# ____________________________________________________________________
# Definitions of ISO 4217 Currencies
# Source: http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm

CURRENCIES = {}


def add_currency(code, numeric, name, countries, significantDigits=5):
    global CURRENCIES
    CURRENCIES[code] = Currency(
        code=code,
        numeric=numeric,
        name=name,
        countries=countries,
        significantDigits=significantDigits)
    return CURRENCIES[code]


def get_currency(code):
    try:
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
AUD = add_currency('AUD', '036', 'Australian Dollar', ['AUSTRALIA', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'HEARD ISLAND AND MCDONALD ISLANDS', 'KIRIBATI', 'NAURU', 'NORFOLK ISLAND', 'TUVALU'])
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
BRL = add_currency('BRL', '986', 'Brazilian Real', ['BRAZIL'])
BSD = add_currency('BSD', '044', 'Bahamian Dollar', ['BAHAMAS'])
BTC = add_currency('BTC', 'Nil', 'Bitcoin', [], 8)
BTN = add_currency('BTN', '064', 'Bhutanese ngultrum', ['BHUTAN'])
BWP = add_currency('BWP', '072', 'Pula', ['BOTSWANA'])
BYR = add_currency('BYR', '974', 'Belarussian Ruble', ['BELARUS'])
BZD = add_currency('BZD', '084', 'Belize Dollar', ['BELIZE'])
CAD = add_currency('CAD', '124', 'Canadian Dollar', ['CANADA'])
CDF = add_currency('CDF', '976', 'Congolese franc', ['DEMOCRATIC REPUBLIC OF CONGO'])
CHF = add_currency('CHF', '756', 'Swiss Franc', ['LIECHTENSTEIN'])
CLP = add_currency('CLP', '152', 'Chilean peso', ['CHILE'])
CNY = add_currency('CNY', '156', 'Yuan Renminbi', ['CHINA'])
COP = add_currency('COP', '170', 'Colombian peso', ['COLOMBIA'])
CRC = add_currency('CRC', '188', 'Costa Rican Colon', ['COSTA RICA'])
CUC = add_currency('CUC', '931', 'Cuban convertible peso', ['CUBA'])
CUP = add_currency('CUP', '192', 'Cuban Peso', ['CUBA'])
CVE = add_currency('CVE', '132', 'Cape Verde Escudo', ['CAPE VERDE'])
CZK = add_currency('CZK', '203', 'Czech Koruna', ['CZECH REPUBLIC'])
DJF = add_currency('DJF', '262', 'Djibouti Franc', ['DJIBOUTI'])
DKK = add_currency('DKK', '208', 'Danish Krone', ['DENMARK', 'FAROE ISLANDS', 'GREENLAND'])
DOP = add_currency('DOP', '214', 'Dominican Peso', ['DOMINICAN REPUBLIC'])
DZD = add_currency('DZD', '012', 'Algerian Dinar', ['ALGERIA'])
EEK = add_currency('EEK', '233', 'Kroon', ['ESTONIA'])
EGP = add_currency('EGP', '818', 'Egyptian Pound', ['EGYPT'])
ERN = add_currency('ERN', '232', 'Nakfa', ['ERITREA'])
ETB = add_currency('ETB', '230', 'Ethiopian Birr', ['ETHIOPIA'])
EUR = add_currency('EUR', '978', 'Euro', ['ANDORRA', 'AUSTRIA', 'BELGIUM', 'FINLAND', 'FRANCE', 'FRENCH GUIANA', 'FRENCH SOUTHERN TERRITORIES', 'GERMANY', 'GREECE', 'GUADELOUPE', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'MARTINIQUE', 'MAYOTTE', 'MONACO', 'MONTENEGRO', 'NETHERLANDS', 'PORTUGAL', 'R.UNION', 'SAINT PIERRE AND MIQUELON', 'SAN MARINO', 'SLOVENIA', 'SPAIN'])
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
IMP = add_currency('IMP', 'Nil', 'Isle of Man pount', ['ISLE OF MAN'])
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
MWK = add_currency('MWK', '454', 'Kwacha', ['MALAWI'])
MXN = add_currency('MXN', '484', 'Mexixan peso', ['MEXICO'])
MYR = add_currency('MYR', '458', 'Malaysian Ringgit', ['MALAYSIA'])
MZN = add_currency('MZN', '943', 'Metical', ['MOZAMBIQUE'])
NAD = add_currency('NAD', '516', 'Namibian Dollar', ['NAMIBIA'])
NGN = add_currency('NGN', '566', 'Naira', ['NIGERIA'])
NIO = add_currency('NIO', '558', 'Cordoba Oro', ['NICARAGUA'])
NOK = add_currency('NOK', '578', 'Norwegian Krone', ['BOUVET ISLAND', 'NORWAY', 'SVALBARD AND JAN MAYEN'])
NPR = add_currency('NPR', '524', 'Nepalese Rupee', ['NEPAL'])
NZD = add_currency('NZD', '554', 'New Zealand Dollar', ['COOK ISLANDS', ', prefix=None, suffix=NoneNEW ZEALAND', 'NIUE', 'PITCAIRN', 'TOKELAU'])
OMR = add_currency('OMR', '512', 'Rial Omani', ['OMAN'])
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
SKK = add_currency('SKK', '703', 'Slovak Koruna', ['SLOVAKIA'])
SLL = add_currency('SLL', '694', 'Leone', ['SIERRA LEONE'])
SOS = add_currency('SOS', '706', 'Somali Shilling', ['SOMALIA'])
SRD = add_currency('SRD', '968', 'Surinam Dollar', ['SURINAME'])
STD = add_currency('STD', '678', 'Dobra', ['SAO TOME AND PRINCIPE'])
SYP = add_currency('SYP', '760', 'Syrian Pound', ['SYRIAN ARAB REPUBLIC'])
SZL = add_currency('SZL', '748', 'Lilangeni', ['SWAZILAND'])
THB = add_currency('THB', '764', 'Baht', ['THAILAND'])
TJS = add_currency('TJS', '972', 'Somoni', ['TAJIKISTAN'])
TMM = add_currency('TMM', '795', 'Manat', ['TURKMENISTAN'])
TND = add_currency('TND', '788', 'Tunisian Dinar', ['TUNISIA'])
TOP = add_currency('TOP', '776', 'Paanga', ['TONGA'])
TRY = add_currency('TRY', '949', 'Turkish Lira', ['TURKEY'])
TTD = add_currency('TTD', '780', 'Trinidad and Tobago Dollar', ['TRINIDAD AND TOBAGO'])
TVD = add_currency('TVD', 'Nil', 'Tuvalu dollar', ['TUVALU'])
TWD = add_currency('TWD', '901', 'New Taiwan Dollar', ['TAIWAN'])
TZS = add_currency('TZS', '834', 'Tanzanian Shilling', ['TANZANIA'])
UAH = add_currency('UAH', '980', 'Hryvnia', ['UKRAINE'])
UGX = add_currency('UGX', '800', 'Uganda Shilling', ['UGANDA'])
USD = add_currency('USD', '840', 'US Dollar', ['AMERICAN SAMOA', 'BRITISH INDIAN OCEAN TERRITORY', 'ECUADOR', 'GUAM', 'MARSHALL ISLANDS', 'MICRONESIA', 'NORTHERN MARIANA ISLANDS', 'PALAU', 'PUERTO RICO', 'TIMOR-LESTE', 'TURKS AND CAICOS ISLANDS', 'UNITED STATES', 'UNITED STATES MINOR OUTLYING ISLANDS', 'VIRGIN ISLANDS (BRITISH)', 'VIRGIN ISLANDS (U.S.)'])
UYU = add_currency('UYU', '858', 'Uruguayan peso', ['URUGUAY'])
UZS = add_currency('UZS', '860', 'Uzbekistan Sum', ['UZBEKISTAN'])
VEF = add_currency('VEF', '937', 'Bolivar Fuerte', ['VENEZUELA'])
VND = add_currency('VND', '704', 'Dong', ['VIET NAM'])
VUV = add_currency('VUV', '548', 'Vatu', ['VANUATU'])
WST = add_currency('WST', '882', 'Tala', ['SAMOA'])
XAF = add_currency('XAF', '950', 'CFA franc BEAC', ['CAMEROON', 'CENTRAL AFRICAN REPUBLIC', 'REPUBLIC OF THE CONGO', 'CHAD', 'EQUATORIAL GUINEA', 'GABON'])
XAG = add_currency('XAG', '961', 'Silver', [])
XAU = add_currency('XAU', '959', 'Gold', [])
XBA = add_currency('XBA', '955', 'Bond Markets Units European Composite Unit (EURCO)', [])
XBB = add_currency('XBB', '956', 'European Monetary Unit (E.M.U.-6)', [])
XBC = add_currency('XBC', '957', 'European Unit of Account 9(E.U.A.-9)', [])
XBD = add_currency('XBD', '958', 'European Unit of Account 17(E.U.A.-17)', [])
XCD = add_currency('XCD', '951', 'East Caribbean Dollar', ['ANGUILLA', 'ANTIGUA AND BARBUDA', 'DOMINICA', 'GRENADA', 'MONTSERRAT', 'SAINT KITTS AND NEVIS', 'SAINT LUCIA', 'SAINT VINCENT AND THE GRENADINES'])
XDR = add_currency('XDR', '960', 'SDR', ['INTERNATIONAL MONETARY FUND (I.M.F)'])
XFO = add_currency('XFO', 'Nil', 'Gold-Franc', [])
XFU = add_currency('XFU', 'Nil', 'UIC-Franc', [])
XOF = add_currency('XOF', '952', 'CFA Franc BCEAO', ['BENIN', 'BURKINA FASO', 'COTE D\'IVOIRE', 'GUINEA-BISSAU', 'MALI', 'NIGER', 'SENEGAL', 'TOGO'])
XPD = add_currency('XPD', '964', 'Palladium', [])
XPF = add_currency('XPF', '953', 'CFP Franc', ['FRENCH POLYNESIA', 'NEW CALEDONIA', 'WALLIS AND FUTUNA'])
XPT = add_currency('XPT', '962', 'Platinum', [])
XTS = add_currency('XTS', '963', 'Codes specifically reserved for testing purposes', [])
YER = add_currency('YER', '886', 'Yemeni Rial', ['YEMEN'])
ZAR = add_currency('ZAR', '710', 'Rand', ['SOUTH AFRICA'])
ZMK = add_currency('ZMK', '894', 'Kwacha', ['ZAMBIA'])
ZWD = add_currency('ZWD', '716', 'Zimbabwe Dollar A/06', ['ZIMBABWE'])
ZWL = add_currency('ZWL', '932', 'Zimbabwe dollar A/09', ['ZIMBABWE'])
ZWN = add_currency('ZWN', '942', 'Zimbabwe dollar A/08', ['ZIMBABWE'])
