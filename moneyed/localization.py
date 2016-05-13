# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from decimal import Decimal, ROUND_HALF_EVEN
import moneyed

DEFAULT = "default"


class CurrencyFormatter(object):

    sign_definitions = {}
    formatting_definitions = {}

    def add_sign_definition(self, locale, currency, prefix='', suffix=''):
        locale = locale.upper()
        currency_code = currency.code.upper()
        if locale not in self.sign_definitions:
            self.sign_definitions[locale] = {}
        self.sign_definitions[locale][currency_code] = (prefix, suffix)

    def add_formatting_definition(self, locale, group_size,
                                  group_separator, decimal_point,
                                  positive_sign, trailing_positive_sign,
                                  negative_sign, trailing_negative_sign,
                                  rounding_method):
        locale = locale.upper()
        self.formatting_definitions[locale] = {
            'group_size': group_size,
            'group_separator': group_separator,
            'decimal_point': decimal_point,
            'positive_sign': positive_sign,
            'trailing_positive_sign': trailing_positive_sign,
            'negative_sign': negative_sign,
            'trailing_negative_sign': trailing_negative_sign,
            'rounding_method': rounding_method}

    def get_sign_definition(self, currency_code, locale):
        currency_code = currency_code.upper()

        if locale.upper() not in self.sign_definitions:
            locale = DEFAULT

        local_set = self.sign_definitions.get(locale.upper())

        if currency_code in local_set:
            return local_set.get(currency_code)
        else:
            return ('', " %s" % currency_code)

    def get_formatting_definition(self, locale):
        locale = locale.upper()
        if locale in self.formatting_definitions:
            return self.formatting_definitions.get(locale)
        else:
            return self.formatting_definitions.get(DEFAULT)

    def format(self, money, include_symbol=True, locale=DEFAULT,
               decimal_places=None, rounding_method=None):
        locale = locale.upper()
        code = money.currency.code.upper()
        prefix, suffix = self.get_sign_definition(code, locale)
        formatting = self.get_formatting_definition(locale)

        if rounding_method is None:
            rounding_method = formatting['rounding_method']

        if decimal_places is None:
            # TODO: Use individual defaults for each currency
            decimal_places = 2

        q = Decimal(10) ** -decimal_places  # 2 places --> '0.01'
        quantized = money.amount.quantize(q, rounding_method)
        negative, digits, e = quantized.as_tuple()

        result = []

        digits = list(map(str, digits))

        build, next = result.append, digits.pop

        # Trailing sign
        if negative:
            build(formatting['trailing_negative_sign'])
        else:
            build(formatting['trailing_positive_sign'])

        # Suffix
        if include_symbol:
            build(suffix)

        # Decimals
        for i in range(decimal_places):
            build(next() if digits else '0')

        # Decimal points
        if decimal_places:
            build(formatting['decimal_point'])

        # Grouped number
        if not digits:
            build('0')
        else:
            i = 0
            while digits:
                build(next())
                i += 1
                if i == formatting['group_size'] and digits:
                    i = 0
                    build(formatting['group_separator'])

        # Prefix
        if include_symbol:
            build(prefix)

        # Sign
        if negative:
            build(formatting['negative_sign'])
        else:
            build(formatting['positive_sign'])

        return ''.join(reversed(result))

_FORMATTER = CurrencyFormatter()

format_money = _FORMATTER.format

_sign = _FORMATTER.add_sign_definition
_format = _FORMATTER.add_formatting_definition

# FORMATTING RULES

_format(DEFAULT, group_size=3, group_separator=",", decimal_point=".",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("en_US", group_size=3, group_separator=",", decimal_point=".",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("de_DE", group_size=3, group_separator=" ", decimal_point=",",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("de_AT", group_size=3, group_separator=" ", decimal_point=",",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("de_CH", group_size=3, group_separator=" ", decimal_point=".",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("sv_SE", group_size=3, group_separator=" ", decimal_point=",",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("pl_PL", group_size=3, group_separator=" ", decimal_point=",",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("en_GB", group_size=3, group_separator=",", decimal_point=".",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)


# CURRENCY SIGNS
# Default currency signs. These can be overridden for locales where
# foreign or local currency signs for one reason or another differ
# from the norm.

# There may be errors here, they have been entered manually. Please
# fork and fix if you find errors.
# Code lives here (2011-05-08): https://github.com/limist/py-moneyed

_sign(DEFAULT, moneyed.CURRENCIES['AED'], prefix='د.إ')
_sign(DEFAULT, moneyed.CURRENCIES['AFN'], suffix='؋')
_sign(DEFAULT, moneyed.CURRENCIES['ALL'], prefix='L')
_sign(DEFAULT, moneyed.CURRENCIES['AMD'], prefix='Դ')
_sign(DEFAULT, moneyed.CURRENCIES['ANG'], prefix='ƒ')
_sign(DEFAULT, moneyed.CURRENCIES['AOA'], prefix='Kz')
_sign(DEFAULT, moneyed.CURRENCIES['ARS'], prefix='ARS$')
_sign(DEFAULT, moneyed.CURRENCIES['AUD'], prefix='A$')
_sign(DEFAULT, moneyed.CURRENCIES['AWG'], prefix='ƒ')
_sign(DEFAULT, moneyed.CURRENCIES['BAM'], prefix='КМ')
_sign(DEFAULT, moneyed.CURRENCIES['BBD'], prefix='Bds$')
_sign(DEFAULT, moneyed.CURRENCIES['BDT'], prefix='৳')
_sign(DEFAULT, moneyed.CURRENCIES['BGN'], prefix='лв')
_sign(DEFAULT, moneyed.CURRENCIES['BHD'], prefix='.د.ب')
_sign(DEFAULT, moneyed.CURRENCIES['BIF'], prefix='FBu')
_sign(DEFAULT, moneyed.CURRENCIES['BMD'], prefix='BD$')
_sign(DEFAULT, moneyed.CURRENCIES['BND'], prefix='B$')
_sign(DEFAULT, moneyed.CURRENCIES['BRL'], prefix='R$')
_sign(DEFAULT, moneyed.CURRENCIES['BSD'], prefix='B$')
_sign(DEFAULT, moneyed.CURRENCIES['BTN'], prefix='Nu.')
_sign(DEFAULT, moneyed.CURRENCIES['BWP'], prefix='P')
_sign(DEFAULT, moneyed.CURRENCIES['BYR'], prefix='Br')
_sign(DEFAULT, moneyed.CURRENCIES['BZD'], prefix='BZ$')
_sign(DEFAULT, moneyed.CURRENCIES['CAD'], prefix='C$')
_sign(DEFAULT, moneyed.CURRENCIES['CDF'], prefix='C₣')
_sign(DEFAULT, moneyed.CURRENCIES['CHF'], prefix='Fr.')
_sign(DEFAULT, moneyed.CURRENCIES['CLP'], prefix='CLP$')
_sign(DEFAULT, moneyed.CURRENCIES['CNY'], prefix='¥')
_sign(DEFAULT, moneyed.CURRENCIES['COP'], prefix='COL$')
_sign(DEFAULT, moneyed.CURRENCIES['CRC'], prefix='₡')
_sign(DEFAULT, moneyed.CURRENCIES['CUC'], prefix='CUC$')
_sign(DEFAULT, moneyed.CURRENCIES['CUP'], prefix='$MN')
_sign(DEFAULT, moneyed.CURRENCIES['CVE'], prefix='Esc')
_sign(DEFAULT, moneyed.CURRENCIES['CZK'], prefix='Kč')
_sign(DEFAULT, moneyed.CURRENCIES['DJF'], prefix='D₣')
_sign(DEFAULT, moneyed.CURRENCIES['DKK'], suffix=' Dkr')
_sign(DEFAULT, moneyed.CURRENCIES['DOP'], prefix='RD$')
_sign(DEFAULT, moneyed.CURRENCIES['DZD'], prefix='دج')
_sign(DEFAULT, moneyed.CURRENCIES['EGP'], prefix='ج.م.')
_sign(DEFAULT, moneyed.CURRENCIES['ERN'], prefix='Nfk')
_sign(DEFAULT, moneyed.CURRENCIES['ETB'], prefix='Br')
_sign(DEFAULT, moneyed.CURRENCIES['EUR'], suffix=' €')
_sign(DEFAULT, moneyed.CURRENCIES['FJD'], prefix='FJ$')
_sign(DEFAULT, moneyed.CURRENCIES['FKP'], prefix='FK£')
_sign(DEFAULT, moneyed.CURRENCIES['GBP'], prefix='GB£')
_sign(DEFAULT, moneyed.CURRENCIES['GEL'], prefix='ლ')
_sign(DEFAULT, moneyed.CURRENCIES['GHS'], prefix='₵')
_sign(DEFAULT, moneyed.CURRENCIES['GIP'], prefix='GIP£')
_sign(DEFAULT, moneyed.CURRENCIES['GMD'], prefix='D')
_sign(DEFAULT, moneyed.CURRENCIES['GNF'], prefix='G₣')
_sign(DEFAULT, moneyed.CURRENCIES['GTQ'], prefix='Q')
_sign(DEFAULT, moneyed.CURRENCIES['GYD'], prefix='G$')
_sign(DEFAULT, moneyed.CURRENCIES['HKD'], prefix='HK$')
_sign(DEFAULT, moneyed.CURRENCIES['HNL'], prefix='L')
_sign(DEFAULT, moneyed.CURRENCIES['HRK'], suffix=' kn')
_sign(DEFAULT, moneyed.CURRENCIES['HTG'], prefix='G')
_sign(DEFAULT, moneyed.CURRENCIES['HUF'], prefix='Ft')
_sign(DEFAULT, moneyed.CURRENCIES['IDR'], prefix='Rp')
_sign(DEFAULT, moneyed.CURRENCIES['ILS'], prefix='₪')
_sign(DEFAULT, moneyed.CURRENCIES['IMP'], prefix='IM£')
_sign(DEFAULT, moneyed.CURRENCIES['INR'], prefix='₹')
_sign(DEFAULT, moneyed.CURRENCIES['IQD'], prefix='ع.د')
_sign(DEFAULT, moneyed.CURRENCIES['IRR'], prefix='ریال')
_sign(DEFAULT, moneyed.CURRENCIES['ISK'], suffix=' Íkr')
_sign(DEFAULT, moneyed.CURRENCIES['JMD'], prefix='J$')
_sign(DEFAULT, moneyed.CURRENCIES['JOD'], prefix='JD')
_sign(DEFAULT, moneyed.CURRENCIES['JPY'], prefix='¥')
_sign(DEFAULT, moneyed.CURRENCIES['KES'], prefix='Ksh')
_sign(DEFAULT, moneyed.CURRENCIES['KGS'], prefix='лв')
_sign(DEFAULT, moneyed.CURRENCIES['KHR'], prefix='៛')
_sign(DEFAULT, moneyed.CURRENCIES['KMF'], prefix='C₣')
_sign(DEFAULT, moneyed.CURRENCIES['KPW'], prefix='₩')
_sign(DEFAULT, moneyed.CURRENCIES['KRW'], prefix='₩')
_sign(DEFAULT, moneyed.CURRENCIES['KWD'], prefix='د.ك')
_sign(DEFAULT, moneyed.CURRENCIES['KYD'], prefix='CI$')
_sign(DEFAULT, moneyed.CURRENCIES['LAK'], prefix='₭')
_sign(DEFAULT, moneyed.CURRENCIES['LBP'], prefix='LL')
_sign(DEFAULT, moneyed.CURRENCIES['LKR'], prefix='₨')
_sign(DEFAULT, moneyed.CURRENCIES['LRD'], prefix='LD$')
_sign(DEFAULT, moneyed.CURRENCIES['LSL'], prefix='M')
_sign(DEFAULT, moneyed.CURRENCIES['LTL'], prefix='Lt')
_sign(DEFAULT, moneyed.CURRENCIES['LVL'], prefix='Ls')
_sign(DEFAULT, moneyed.CURRENCIES['LYD'], prefix='ل.د')
_sign(DEFAULT, moneyed.CURRENCIES['MAD'], prefix='د.م.')
_sign(DEFAULT, moneyed.CURRENCIES['MGA'], prefix='Ar')
_sign(DEFAULT, moneyed.CURRENCIES['MKD'], prefix='ден')
_sign(DEFAULT, moneyed.CURRENCIES['MMK'], prefix='K')
_sign(DEFAULT, moneyed.CURRENCIES['MNT'], prefix='₮')
_sign(DEFAULT, moneyed.CURRENCIES['MOP'], prefix='MOP$')
_sign(DEFAULT, moneyed.CURRENCIES['MRO'], prefix='UM')
_sign(DEFAULT, moneyed.CURRENCIES['MUR'], prefix='₨')
_sign(DEFAULT, moneyed.CURRENCIES['MVR'], prefix='Rf.')
_sign(DEFAULT, moneyed.CURRENCIES['MWK'], prefix='MK')
_sign(DEFAULT, moneyed.CURRENCIES['MXN'], prefix='Mex$')
_sign(DEFAULT, moneyed.CURRENCIES['MYR'], prefix='RM')
_sign(DEFAULT, moneyed.CURRENCIES['MZN'], prefix='MT')
_sign(DEFAULT, moneyed.CURRENCIES['NAD'], prefix='N$')
_sign(DEFAULT, moneyed.CURRENCIES['NGN'], prefix='₦')
_sign(DEFAULT, moneyed.CURRENCIES['NIO'], prefix='C$')
_sign(DEFAULT, moneyed.CURRENCIES['NOK'], suffix=' Nkr')
_sign(DEFAULT, moneyed.CURRENCIES['NPR'], prefix='₨')
_sign(DEFAULT, moneyed.CURRENCIES['NZD'], prefix='NZ$')
_sign(DEFAULT, moneyed.CURRENCIES['OMR'], prefix='ر.ع.')
_sign(DEFAULT, moneyed.CURRENCIES['PEN'], prefix='S/.')
_sign(DEFAULT, moneyed.CURRENCIES['PGK'], prefix='K')
_sign(DEFAULT, moneyed.CURRENCIES['PHP'], prefix='₱')
_sign(DEFAULT, moneyed.CURRENCIES['PKR'], prefix='₨')
_sign(DEFAULT, moneyed.CURRENCIES['PLN'], suffix=' zł')
_sign(DEFAULT, moneyed.CURRENCIES['PYG'], prefix='₲')
_sign(DEFAULT, moneyed.CURRENCIES['QAR'], prefix='ر.ق')
_sign(DEFAULT, moneyed.CURRENCIES['RSD'], prefix='RSD ')
_sign(DEFAULT, moneyed.CURRENCIES['RUB'], prefix='руб.')
_sign(DEFAULT, moneyed.CURRENCIES['RWF'], prefix='FRw')
_sign(DEFAULT, moneyed.CURRENCIES['SAR'], prefix='ر.س')
_sign(DEFAULT, moneyed.CURRENCIES['SBD'], prefix='SI$')
_sign(DEFAULT, moneyed.CURRENCIES['SCR'], prefix='SRe')
_sign(DEFAULT, moneyed.CURRENCIES['SDG'], prefix='S£')
_sign(DEFAULT, moneyed.CURRENCIES['SEK'], suffix=' Skr')
_sign(DEFAULT, moneyed.CURRENCIES['SGD'], prefix='S$')
_sign(DEFAULT, moneyed.CURRENCIES['SHP'], prefix='SH£')
_sign(DEFAULT, moneyed.CURRENCIES['SLL'], prefix='Le')
_sign(DEFAULT, moneyed.CURRENCIES['SOS'], prefix='Sh.So.')
_sign(DEFAULT, moneyed.CURRENCIES['SRD'], prefix='SRD$')
_sign(DEFAULT, moneyed.CURRENCIES['STD'], prefix='Db')
_sign(DEFAULT, moneyed.CURRENCIES['SYP'], prefix='£S')
_sign(DEFAULT, moneyed.CURRENCIES['SZL'], prefix='E')
_sign(DEFAULT, moneyed.CURRENCIES['THB'], prefix='฿')
_sign(DEFAULT, moneyed.CURRENCIES['TND'], prefix='د.ت')
_sign(DEFAULT, moneyed.CURRENCIES['TOP'], prefix='TOP$')
_sign(DEFAULT, moneyed.CURRENCIES['TRY'], prefix='₺')
_sign(DEFAULT, moneyed.CURRENCIES['TTD'], prefix='TT$')
_sign(DEFAULT, moneyed.CURRENCIES['TWD'], prefix='NT$')
_sign(DEFAULT, moneyed.CURRENCIES['UAH'], prefix='₴')
_sign(DEFAULT, moneyed.CURRENCIES['UGX'], prefix='USh')
_sign(DEFAULT, moneyed.CURRENCIES['USD'], prefix='US$')
_sign(DEFAULT, moneyed.CURRENCIES['UYU'], prefix='$U')
_sign(DEFAULT, moneyed.CURRENCIES['VEF'], prefix='Bs.')
_sign(DEFAULT, moneyed.CURRENCIES['VND'], prefix='₫')
_sign(DEFAULT, moneyed.CURRENCIES['VUV'], prefix='VT')
_sign(DEFAULT, moneyed.CURRENCIES['WST'], prefix='WS$')
_sign(DEFAULT, moneyed.CURRENCIES['XAF'], prefix='FCFA')
_sign(DEFAULT, moneyed.CURRENCIES['XCD'], prefix='EC$')
_sign(DEFAULT, moneyed.CURRENCIES['XDR'], prefix='SDR')
_sign(DEFAULT, moneyed.CURRENCIES['XOF'], prefix='CFA')
_sign(DEFAULT, moneyed.CURRENCIES['ZAR'], prefix='R')
_sign(DEFAULT, moneyed.CURRENCIES['ZMK'], prefix='ZK')
_sign(DEFAULT, moneyed.CURRENCIES['ZMW'], prefix='ZK')
_sign(DEFAULT, moneyed.CURRENCIES['ZWL'], prefix='Z$')

_sign('en_US', moneyed.CURRENCIES['USD'], prefix='$')
_sign('en_GB', moneyed.CURRENCIES['GBP'], prefix='£')
_sign('sv_SE', moneyed.CURRENCIES['SEK'], prefix=' kr')
_sign('pl_PL', moneyed.CURRENCIES['PLN'], suffix=' zł')
_sign('de_DE', moneyed.CURRENCIES['EUR'], suffix=' €')
_sign('de_AT', moneyed.CURRENCIES['EUR'], suffix=' €')
_sign('de_CH', moneyed.CURRENCIES['CHF'], prefix='Fr.')

# Adding translations for missing currencies
_sign('en_US', moneyed.CURRENCIES['KWD'], prefix='KD')
_sign('en_US', moneyed.CURRENCIES['BHD'], prefix='BD')
_sign('en_US', moneyed.CURRENCIES['SAR'], prefix='SR')
_sign('en_US', moneyed.CURRENCIES['DZD'], prefix='DA')
_sign('en_US', moneyed.CURRENCIES['LYD'], prefix='LD')
_sign('en_US', moneyed.CURRENCIES['TND'], prefix='DT')
_sign('en_US', moneyed.CURRENCIES['AED'], prefix='Dhs')
_sign('en_US', moneyed.CURRENCIES['EGP'], prefix='L.E.')
_sign('en_US', moneyed.CURRENCIES['QAR'], prefix='QR')
