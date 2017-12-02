# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from decimal import Decimal, ROUND_HALF_EVEN
import moneyed

DEFAULT = "DEFAULT"


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
            ret = self.sign_definitions.get(DEFAULT).get(currency_code)
            return ret if ret is not None else ('', " %s" % currency_code)

    def get_formatting_definition(self, locale):
        if locale.upper() not in self.formatting_definitions:
            locale = DEFAULT
        return self.formatting_definitions.get(locale.upper())

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

_format("fr_FR", group_size=3, group_separator=" ", decimal_point=",",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("fr_CA", group_size=3, group_separator=" ", decimal_point=",",
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

_format('es_BO', group_size=3, group_separator=".", decimal_point=",",
        positive_sign="",  trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("nl_NL", group_size=3, group_separator=".", decimal_point=",",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("nb_NO", group_size=3, group_separator=" ", decimal_point=",",
        positive_sign="", trailing_positive_sign="",
        negative_sign="-", trailing_negative_sign="",
        rounding_method=ROUND_HALF_EVEN)

_format("nn_NO", group_size=3, group_separator=" ", decimal_point=",",
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

_sign(DEFAULT, moneyed.AED, prefix='د.إ')
_sign(DEFAULT, moneyed.AFN, suffix='؋')
_sign(DEFAULT, moneyed.ALL, prefix='L')
_sign(DEFAULT, moneyed.AMD, prefix='Դ')
_sign(DEFAULT, moneyed.ANG, prefix='ƒ')
_sign(DEFAULT, moneyed.AOA, prefix='Kz')
_sign(DEFAULT, moneyed.ARS, prefix='ARS$')
_sign(DEFAULT, moneyed.AUD, prefix='A$')
_sign(DEFAULT, moneyed.AWG, prefix='ƒ')
_sign(DEFAULT, moneyed.BAM, prefix='КМ')
_sign(DEFAULT, moneyed.BBD, prefix='Bds$')
_sign(DEFAULT, moneyed.BDT, prefix='৳')
_sign(DEFAULT, moneyed.BGN, prefix='лв')
_sign(DEFAULT, moneyed.BHD, prefix='.د.ب')
_sign(DEFAULT, moneyed.BIF, prefix='FBu')
_sign(DEFAULT, moneyed.BMD, prefix='BD$')
_sign(DEFAULT, moneyed.BND, prefix='B$')
_sign(DEFAULT, moneyed.BOB, prefix='Bs.')
_sign(DEFAULT, moneyed.BOV, prefix='Bs.')
_sign(DEFAULT, moneyed.BRL, prefix='R$')
_sign(DEFAULT, moneyed.BSD, prefix='B$')
_sign(DEFAULT, moneyed.BTN, prefix='Nu.')
_sign(DEFAULT, moneyed.BWP, prefix='P')
_sign(DEFAULT, moneyed.BYN, prefix='Br')
_sign(DEFAULT, moneyed.BYR, prefix='Br')
_sign(DEFAULT, moneyed.BZD, prefix='BZ$')
_sign(DEFAULT, moneyed.CAD, prefix='C$')
_sign(DEFAULT, moneyed.CDF, prefix='C₣')
_sign(DEFAULT, moneyed.CHE, prefix='CHE')
_sign(DEFAULT, moneyed.CHF, prefix='Fr.')
_sign(DEFAULT, moneyed.CHW, prefix='CHW')
_sign(DEFAULT, moneyed.CLF, prefix='UF')
_sign(DEFAULT, moneyed.CLP, prefix='CLP$')
_sign(DEFAULT, moneyed.CNY, prefix='¥')
_sign(DEFAULT, moneyed.COP, prefix='COL$')
_sign(DEFAULT, moneyed.COU, prefix='COU')
_sign(DEFAULT, moneyed.CRC, prefix='₡')
_sign(DEFAULT, moneyed.CUC, prefix='CUC$')
_sign(DEFAULT, moneyed.CUP, prefix='$MN')
_sign(DEFAULT, moneyed.CVE, prefix='Esc')
_sign(DEFAULT, moneyed.CZK, suffix=' Kč')
_sign(DEFAULT, moneyed.DJF, prefix='D₣')
_sign(DEFAULT, moneyed.DKK, suffix=' Dkr')
_sign(DEFAULT, moneyed.DOP, prefix='RD$')
_sign(DEFAULT, moneyed.DZD, prefix='دج')
_sign(DEFAULT, moneyed.EGP, prefix='ج.م.')
_sign(DEFAULT, moneyed.ERN, prefix='Nfk')
_sign(DEFAULT, moneyed.ETB, prefix='Br')
_sign(DEFAULT, moneyed.EUR, suffix=' €')
_sign(DEFAULT, moneyed.FJD, prefix='FJ$')
_sign(DEFAULT, moneyed.FKP, prefix='FK£')
_sign(DEFAULT, moneyed.GBP, prefix='GB£')
_sign(DEFAULT, moneyed.GEL, prefix='ლ')
_sign(DEFAULT, moneyed.GHS, prefix='₵')
_sign(DEFAULT, moneyed.GIP, prefix='GIP£')
_sign(DEFAULT, moneyed.GMD, prefix='D')
_sign(DEFAULT, moneyed.GNF, prefix='G₣')
_sign(DEFAULT, moneyed.GTQ, prefix='Q')
_sign(DEFAULT, moneyed.GYD, prefix='G$')
_sign(DEFAULT, moneyed.HKD, prefix='HK$')
_sign(DEFAULT, moneyed.HNL, prefix='L')
_sign(DEFAULT, moneyed.HRK, suffix=' kn')
_sign(DEFAULT, moneyed.HTG, prefix='G')
_sign(DEFAULT, moneyed.HUF, prefix='Ft')
_sign(DEFAULT, moneyed.IDR, prefix='Rp')
_sign(DEFAULT, moneyed.ILS, prefix='₪')
_sign(DEFAULT, moneyed.IMP, prefix='IM£')
_sign(DEFAULT, moneyed.INR, prefix='₹')
_sign(DEFAULT, moneyed.IQD, prefix='ع.د')
_sign(DEFAULT, moneyed.IRR, prefix='ریال')
_sign(DEFAULT, moneyed.ISK, suffix=' Íkr')
_sign(DEFAULT, moneyed.JMD, prefix='J$')
_sign(DEFAULT, moneyed.JOD, prefix='JD')
_sign(DEFAULT, moneyed.JPY, prefix='¥')
_sign(DEFAULT, moneyed.KES, prefix='Ksh')
_sign(DEFAULT, moneyed.KGS, prefix='лв')
_sign(DEFAULT, moneyed.KHR, prefix='៛')
_sign(DEFAULT, moneyed.KMF, prefix='C₣')
_sign(DEFAULT, moneyed.KPW, prefix='₩')
_sign(DEFAULT, moneyed.KRW, prefix='₩')
_sign(DEFAULT, moneyed.KWD, prefix='د.ك')
_sign(DEFAULT, moneyed.KYD, prefix='CI$')
_sign(DEFAULT, moneyed.LAK, prefix='₭')
_sign(DEFAULT, moneyed.LBP, prefix='LL')
_sign(DEFAULT, moneyed.LKR, prefix='₨')
_sign(DEFAULT, moneyed.LRD, prefix='LD$')
_sign(DEFAULT, moneyed.LSL, prefix='M')
_sign(DEFAULT, moneyed.LTL, prefix='Lt')
_sign(DEFAULT, moneyed.LVL, prefix='Ls')
_sign(DEFAULT, moneyed.LYD, prefix='ل.د')
_sign(DEFAULT, moneyed.MAD, prefix='د.م.')
_sign(DEFAULT, moneyed.MGA, prefix='Ar')
_sign(DEFAULT, moneyed.MKD, prefix='ден')
_sign(DEFAULT, moneyed.MMK, prefix='K')
_sign(DEFAULT, moneyed.MNT, prefix='₮')
_sign(DEFAULT, moneyed.MOP, prefix='MOP$')
_sign(DEFAULT, moneyed.MRO, prefix='UM')
_sign(DEFAULT, moneyed.MUR, prefix='₨')
_sign(DEFAULT, moneyed.MVR, prefix='Rf.')
_sign(DEFAULT, moneyed.MWK, prefix='MK')
_sign(DEFAULT, moneyed.MXN, prefix='Mex$')
_sign(DEFAULT, moneyed.MXV, prefix='UDI')
_sign(DEFAULT, moneyed.MYR, prefix='RM')
_sign(DEFAULT, moneyed.MZN, prefix='MT')
_sign(DEFAULT, moneyed.NAD, prefix='N$')
_sign(DEFAULT, moneyed.NGN, prefix='₦')
_sign(DEFAULT, moneyed.NIO, prefix='C$')
_sign(DEFAULT, moneyed.NOK, suffix=' Nkr')
_sign(DEFAULT, moneyed.NPR, prefix='₨')
_sign(DEFAULT, moneyed.NZD, prefix='NZ$')
_sign(DEFAULT, moneyed.OMR, prefix='ر.ع.')
_sign(DEFAULT, moneyed.PAB, prefix='B/.')
_sign(DEFAULT, moneyed.PEN, prefix='S/.')
_sign(DEFAULT, moneyed.PGK, prefix='K')
_sign(DEFAULT, moneyed.PHP, prefix='₱')
_sign(DEFAULT, moneyed.PKR, prefix='₨')
_sign(DEFAULT, moneyed.PLN, suffix=' zł')
_sign(DEFAULT, moneyed.PYG, prefix='₲')
_sign(DEFAULT, moneyed.QAR, prefix='ر.ق')
_sign(DEFAULT, moneyed.RSD, prefix='RSD ')
_sign(DEFAULT, moneyed.RUB, suffix=' руб.')
_sign(DEFAULT, moneyed.RWF, prefix='FRw')
_sign(DEFAULT, moneyed.SAR, prefix='ر.س')
_sign(DEFAULT, moneyed.SBD, prefix='SI$')
_sign(DEFAULT, moneyed.SCR, prefix='SRe')
_sign(DEFAULT, moneyed.SDG, prefix='S£')
_sign(DEFAULT, moneyed.SEK, suffix=' Skr')
_sign(DEFAULT, moneyed.SGD, prefix='S$')
_sign(DEFAULT, moneyed.SHP, prefix='SH£')
_sign(DEFAULT, moneyed.SLL, prefix='Le')
_sign(DEFAULT, moneyed.SOS, prefix='Sh.So.')
_sign(DEFAULT, moneyed.SRD, prefix='SRD$')
_sign(DEFAULT, moneyed.SSP, prefix='£')
_sign(DEFAULT, moneyed.STD, prefix='Db')
_sign(DEFAULT, moneyed.SVC, prefix='₡')
_sign(DEFAULT, moneyed.SYP, prefix='£S')
_sign(DEFAULT, moneyed.SZL, prefix='E')
_sign(DEFAULT, moneyed.THB, prefix='฿')
_sign(DEFAULT, moneyed.TND, prefix='د.ت')
_sign(DEFAULT, moneyed.TMT, prefix='m')
_sign(DEFAULT, moneyed.TOP, prefix='TOP$')
_sign(DEFAULT, moneyed.TRY, prefix='₺')
_sign(DEFAULT, moneyed.TTD, prefix='TT$')
_sign(DEFAULT, moneyed.TVD, prefix='$T')
_sign(DEFAULT, moneyed.TWD, prefix='NT$')
_sign(DEFAULT, moneyed.UAH, prefix='₴')
_sign(DEFAULT, moneyed.UGX, prefix='USh')
_sign(DEFAULT, moneyed.USD, prefix='US$')
_sign(DEFAULT, moneyed.USN, prefix='USN')
_sign(DEFAULT, moneyed.UYI, prefix='$U')
_sign(DEFAULT, moneyed.UYU, prefix='$U')
_sign(DEFAULT, moneyed.VEF, prefix='Bs.')
_sign(DEFAULT, moneyed.VND, prefix='₫')
_sign(DEFAULT, moneyed.VUV, prefix='VT')
_sign(DEFAULT, moneyed.WST, prefix='WS$')
_sign(DEFAULT, moneyed.XAF, prefix='FCFA')
_sign(DEFAULT, moneyed.XCD, prefix='EC$')
_sign(DEFAULT, moneyed.XDR, prefix='SDR')
_sign(DEFAULT, moneyed.XOF, prefix='CFA')
_sign(DEFAULT, moneyed.XSU, prefix='Sucre')
_sign(DEFAULT, moneyed.XUA, prefix='XUA')
_sign(DEFAULT, moneyed.XXX, prefix='XXX')
_sign(DEFAULT, moneyed.ZAR, prefix='R')
_sign(DEFAULT, moneyed.ZMK, prefix='ZK')
_sign(DEFAULT, moneyed.ZMW, prefix='ZK')
_sign(DEFAULT, moneyed.ZWL, prefix='Z$')

_sign('en_US', moneyed.USD, prefix='$')
_sign('en_GB', moneyed.GBP, prefix='£')
_sign('en_GB', moneyed.EUR, prefix='€')
_sign('sv_SE', moneyed.SEK, prefix='kr ')
_sign('pl_PL', moneyed.PLN, suffix=' zł')
_sign('de_DE', moneyed.EUR, suffix=' €')
_sign('de_AT', moneyed.EUR, suffix=' €')
_sign('de_CH', moneyed.CHF, prefix='Fr.')
_sign('fr_FR', moneyed.EUR, suffix=' €')
_sign('fr_FR', moneyed.USD, suffix=' $ US')
_sign('fr_CA', moneyed.USD, suffix=' $ US')
_sign('fr_FR', moneyed.CAD, suffix=' $ CA')
_sign('fr_CA', moneyed.CAD, suffix=' $')
_sign('fr_CA', moneyed.EUR, suffix=' €')
_sign('nl_NL', moneyed.EUR, prefix='€ ')
_sign('nb_NO', moneyed.NOK, prefix='kr ')
_sign('nn_NO', moneyed.NOK, prefix='kr ')

# Adding translations for missing currencies
_sign('en_US', moneyed.KWD, prefix='KD')
_sign('en_US', moneyed.BHD, prefix='BD')
_sign('en_US', moneyed.SAR, prefix='SR')
_sign('en_US', moneyed.DZD, prefix='DA')
_sign('en_US', moneyed.LYD, prefix='LD')
_sign('en_US', moneyed.TND, prefix='DT')
_sign('en_US', moneyed.AED, prefix='Dhs')
_sign('en_US', moneyed.EGP, prefix='L.E.')
_sign('en_US', moneyed.QAR, prefix='QR')
