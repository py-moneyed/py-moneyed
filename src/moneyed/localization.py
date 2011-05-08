# -*- coding: utf-8 -*-

from decimal import Decimal, ROUND_HALF_EVEN
import moneyed

DEFAULT = "default"

class CurrencyFormatter(object):
    
    sign_definitions = {}
    formatting_definitions = {}
    
    def add_sign_definition(self, locale, currency, prefix=u'', suffix=u''):
        locale = locale.upper()
        currency_code = currency.code.upper()
        if not self.sign_definitions.has_key(locale):
            self.sign_definitions[locale] = {}
        self.sign_definitions[locale][currency_code] = (prefix, suffix)
    
    def add_formatting_definition(self, locale, group_size, group_separator, 
                                  decimal_point, positive_sign, trailing_positive_sign,
                                  negative_sign, trailing_negative_sign, rounding_method):
        locale = locale.upper()
        self.formatting_definitions[locale] = { 
            'group_size' : group_size,
            'group_separator' : group_separator,
            'decimal_point' : decimal_point,
            'positive_sign' : positive_sign,
            'trailing_positive_sign' : trailing_positive_sign,
            'negative_sign' : negative_sign,
            'trailing_negative_sign' : trailing_negative_sign,
            'rounding_method' : rounding_method }
    
    def get_sign_definition(self, currency_code, locale):
        locale = locale.upper()
        currency_code = currency_code.upper()
        local_set = self.sign_definitions.get(locale) if self.sign_definitions.has_key(locale) else self.sign_definitions.get(DEFAULT)
        return local_set.get(currency_code) if local_set.has_key(currency_code) else ('', " %s" % currency_code)
    
    def get_formatting_definition(self, locale):
        locale = locale.upper()
        return self.formatting_definitions.get(locale) if self.formatting_definitions.has_key(locale) else self.formatting_definitions.get(DEFAULT)
    
    def format(self, money, include_symbol=True, locale=DEFAULT, decimal_places=None, rounding_method=None):
        
        locale = locale.upper()

        prefix, suffix = self.get_sign_definition(money.currency.code.upper(), locale)
        formatting = self.get_formatting_definition(locale)
        
        if rounding_method is None:
            rounding_method = formatting['rounding_method']
            
        if decimal_places is None:
            # TODO: Add decimal places to each currency definition, use as default here.
            decimal_places = 2
        
        q = Decimal(10) ** -decimal_places # 2 places --> '0.01'
        sign, digits, exp = money.amount.quantize(q, rounding_method).as_tuple()
        
        result = []
        digits = map(str, digits)
        build, next = result.append, digits.pop
        
        # Trailing sign
        build(formatting['trailing_negative_sign'] if sign else formatting['trailing_positive_sign'])
        
        # Suffix
        if include_symbol:
            build(suffix)
        
        # Decimals
        for i in range(decimal_places):
            build(next() if digits else '0')
            
        # Decimal points
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
        build(formatting['negative_sign'] if sign else formatting['positive_sign'])
        
        return u''.join(reversed(result))
    
_FORMATTER = CurrencyFormatter()

format_money = _FORMATTER.format

_sign   = _FORMATTER.add_sign_definition
_format = _FORMATTER.add_formatting_definition

## FORMATTING RULES

_format(DEFAULT, group_size=3, group_separator=",", decimal_point=".", 
                 positive_sign="",  trailing_positive_sign="",
                 negative_sign="-", trailing_negative_sign="", rounding_method=ROUND_HALF_EVEN)

_format("en_US", group_size=3, group_separator=",", decimal_point=".", 
                 positive_sign="",  trailing_positive_sign="",
                 negative_sign="-", trailing_negative_sign="", rounding_method=ROUND_HALF_EVEN)

_format("sv_SE", group_size=3, group_separator=" ", decimal_point=",", 
                 positive_sign="",  trailing_positive_sign="",
                 negative_sign="-", trailing_negative_sign="", rounding_method=ROUND_HALF_EVEN)

## CURRENCY SIGNS
# Default currency signs. These can be overridden for locales where 
# foreign or local currency signs for one reason or another differ from the norm.

_sign(DEFAULT, moneyed.AFN, suffix=u'؋')
_sign(DEFAULT, moneyed.MGA, prefix=u'Ar')
_sign(DEFAULT, moneyed.EUR, suffix=u' €')
_sign(DEFAULT, moneyed.ISK, suffix=u' kr')
_sign(DEFAULT, moneyed.SEK, suffix=u' kr')
_sign(DEFAULT, moneyed.DKK, suffix=u' kr')
_sign(DEFAULT, moneyed.NOK, suffix=u' kr')
_sign(DEFAULT, moneyed.USD, prefix=u'$')

_sign(DEFAULT, moneyed.THB, prefix=u'฿')
_sign(DEFAULT, moneyed.ETB, prefix=u'Br')
_sign(DEFAULT, moneyed.BYR, prefix=u'Br')
_sign(DEFAULT, moneyed.VEF, prefix=u'Bs.')
_sign(DEFAULT, moneyed.GHS, prefix=u'₵')
_sign(DEFAULT, moneyed.CRC, prefix=u'₡')
_sign(DEFAULT, moneyed.GMD, prefix=u'D')
_sign(DEFAULT, moneyed.MKD, prefix=u'ден')
_sign(DEFAULT, moneyed.DZD, prefix=u'دج')
_sign(DEFAULT, moneyed.BHD, prefix=u'.د.ب')
_sign(DEFAULT, moneyed.IQD, prefix=u'ع.د')
_sign(DEFAULT, moneyed.JOD, prefix=u'JD')
_sign(DEFAULT, moneyed.KWD, prefix=u'د.ك')
_sign(DEFAULT, moneyed.LYD, prefix=u'ل.د')
_sign(DEFAULT, moneyed.RSD, prefix=u'дин')
_sign(DEFAULT, moneyed.TND, prefix=u'د.ت')
_sign(DEFAULT, moneyed.MAD, prefix=u'د.م.')
_sign(DEFAULT, moneyed.AED, prefix=u'د.إ')
_sign(DEFAULT, moneyed.STD, prefix=u'Db')
_sign(DEFAULT, moneyed.AUD, prefix=u'$')
_sign(DEFAULT, moneyed.BSD, prefix=u'$')
_sign(DEFAULT, moneyed.BBD, prefix=u'$')
_sign(DEFAULT, moneyed.BZD, prefix=u'$')
_sign(DEFAULT, moneyed.BMD, prefix=u'$')
_sign(DEFAULT, moneyed.BND, prefix=u'$')
_sign(DEFAULT, moneyed.CAD, prefix=u'$')
_sign(DEFAULT, moneyed.KYD, prefix=u'$')
_sign(DEFAULT, moneyed.XCD, prefix=u'$')
_sign(DEFAULT, moneyed.FJD, prefix=u'$')
_sign(DEFAULT, moneyed.GYD, prefix=u'$')
_sign(DEFAULT, moneyed.HKD, prefix=u'$')
_sign(DEFAULT, moneyed.JMD, prefix=u'$')
_sign(DEFAULT, moneyed.LRD, prefix=u'$')
_sign(DEFAULT, moneyed.NAD, prefix=u'N$')
_sign(DEFAULT, moneyed.NZD, prefix=u'$')
_sign(DEFAULT, moneyed.SGD, prefix=u'$')
_sign(DEFAULT, moneyed.SBD, prefix=u'$')
_sign(DEFAULT, moneyed.SRD, prefix=u'$')
_sign(DEFAULT, moneyed.TWD, prefix=u'$')
_sign(DEFAULT, moneyed.TTD, prefix=u'$')
_sign(DEFAULT, moneyed.TVD, prefix=u'$')
_sign(DEFAULT, moneyed.ZWL, prefix=u'$')
_sign(DEFAULT, moneyed.ARS, prefix=u'$')
_sign(DEFAULT, moneyed.CLP, prefix=u'$')
_sign(DEFAULT, moneyed.COP, prefix=u'$')
_sign(DEFAULT, moneyed.CUP, prefix=u'$')
_sign(DEFAULT, moneyed.CUC, prefix=u'$')
_sign(DEFAULT, moneyed.DOP, prefix=u'$')
_sign(DEFAULT, moneyed.MXN, prefix=u'$')
_sign(DEFAULT, moneyed.UYU, prefix=u'$')
_sign(DEFAULT, moneyed.NIO, prefix=u'$')
_sign(DEFAULT, moneyed.TOP, prefix=u'$')
_sign(DEFAULT, moneyed.VND, prefix=u'₫')
_sign(DEFAULT, moneyed.AMD, prefix=u'Դ')
_sign(DEFAULT, moneyed.CVE, prefix=u'Esc')
_sign(DEFAULT, moneyed.AWG, prefix=u'ƒ')
_sign(DEFAULT, moneyed.ANG, prefix=u'ƒ')
_sign(DEFAULT, moneyed.HUF, prefix=u'Ft')
_sign(DEFAULT, moneyed.BIF, prefix=u'FBu')
_sign(DEFAULT, moneyed.XAF, prefix=u'FCFA')
_sign(DEFAULT, moneyed.KMF, prefix=u'₣')
_sign(DEFAULT, moneyed.CDF, prefix=u'₣')
_sign(DEFAULT, moneyed.DJF, prefix=u'₣')
_sign(DEFAULT, moneyed.GNF, prefix=u'₣')
_sign(DEFAULT, moneyed.CHF, prefix=u'₣')
_sign(DEFAULT, moneyed.RWF, prefix=u'FRw')
_sign(DEFAULT, moneyed.XOF, prefix=u'CFA') 
_sign(DEFAULT, moneyed.HTG, prefix=u'G')
_sign(DEFAULT, moneyed.PYG, prefix=u'₲')
_sign(DEFAULT, moneyed.UAH, prefix=u'₴')
_sign(DEFAULT, moneyed.LAK, prefix=u'₭')
_sign(DEFAULT, moneyed.CZK, prefix=u'Kč')
_sign(DEFAULT, moneyed.HRK, suffix=u'kn')
_sign(DEFAULT, moneyed.MWK, prefix=u'MK')
_sign(DEFAULT, moneyed.ZMK, prefix=u'ZK')
_sign(DEFAULT, moneyed.AOA, prefix=u'Kz')
_sign(DEFAULT, moneyed.MMK, prefix=u'K')
_sign(DEFAULT, moneyed.PGK, prefix=u'K')
_sign(DEFAULT, moneyed.GEL, prefix=u'ლ')
_sign(DEFAULT, moneyed.LVL, prefix=u'Ls')
_sign(DEFAULT, moneyed.ALL, prefix=u'L')
_sign(DEFAULT, moneyed.HNL, prefix=u'L')
_sign(DEFAULT, moneyed.SLL, prefix=u'Le')
_sign(DEFAULT, moneyed.SZL, prefix=u'E')
_sign(DEFAULT, moneyed.TRY, prefix=u'TL')
_sign(DEFAULT, moneyed.LTL, prefix=u'Lt')
_sign(DEFAULT, moneyed.LSL, prefix=u'M')
_sign(DEFAULT, moneyed.BAM, prefix=u'КМ')
_sign(DEFAULT, moneyed.MZN, prefix=u'MT')
_sign(DEFAULT, moneyed.ERN, prefix=u'Nfk')
_sign(DEFAULT, moneyed.NGN, prefix=u'₦')
_sign(DEFAULT, moneyed.BTN, prefix=u'Nu.')
_sign(DEFAULT, moneyed.MRO, prefix=u'UM')
_sign(DEFAULT, moneyed.MOP, prefix=u'MOP$')
_sign(DEFAULT, moneyed.PHP, prefix=u'₱')
_sign(DEFAULT, moneyed.GBP, prefix=u'£')
_sign(DEFAULT, moneyed.FKP, prefix=u'£')
_sign(DEFAULT, moneyed.GIP, prefix=u'£')
_sign(DEFAULT, moneyed.LBP, prefix=u'£')
_sign(DEFAULT, moneyed.IMP, prefix=u'£')
_sign(DEFAULT, moneyed.SHP, prefix=u'£') 
_sign(DEFAULT, moneyed.SDG, prefix=u'£')
_sign(DEFAULT, moneyed.SYP, prefix=u'£')
_sign(DEFAULT, moneyed.EGP, prefix=u'ج.م.')
_sign(DEFAULT, moneyed.BWP, prefix=u'P')
_sign(DEFAULT, moneyed.GTQ, prefix=u'Q')
_sign(DEFAULT, moneyed.ZAR, prefix=u'R')
_sign(DEFAULT, moneyed.BRL, prefix=u'R$')
_sign(DEFAULT, moneyed.IRR, prefix=u'ریال')
_sign(DEFAULT, moneyed.OMR, prefix=u'ر.ع.')
_sign(DEFAULT, moneyed.QAR, prefix=u'ر.ق')
_sign(DEFAULT, moneyed.SAR, prefix=u'ر.س')
_sign(DEFAULT, moneyed.KHR, prefix=u'៛')
_sign(DEFAULT, moneyed.MYR, prefix=u'RM')
_sign(DEFAULT, moneyed.RUB, prefix=u'руб.')
_sign(DEFAULT, moneyed.MVR, prefix=u'Rf.')
_sign(DEFAULT, moneyed.INR, prefix=u'₹')
_sign(DEFAULT, moneyed.MUR, prefix=u'₨')
_sign(DEFAULT, moneyed.NPR, prefix=u'₨')
_sign(DEFAULT, moneyed.PKR, prefix=u'₨')
_sign(DEFAULT, moneyed.LKR, prefix=u'₨')
_sign(DEFAULT, moneyed.SCR, prefix=u'SRe')
_sign(DEFAULT, moneyed.IDR, prefix=u'Rp')
_sign(DEFAULT, moneyed.ILS, prefix=u'₪')
_sign(DEFAULT, moneyed.KES, prefix=u'Ksh')
_sign(DEFAULT, moneyed.SOS, prefix=u'Sh.So.')
_sign(DEFAULT, moneyed.UGX, prefix=u'USh')
_sign(DEFAULT, moneyed.PEN, prefix=u'S/.')
_sign(DEFAULT, moneyed.XDR, prefix=u'SDR')
_sign(DEFAULT, moneyed.BGN, prefix=u'лв')
_sign(DEFAULT, moneyed.KGS, prefix=u'лв')
_sign(DEFAULT, moneyed.BDT, prefix=u'৳')
_sign(DEFAULT, moneyed.WST, prefix=u'WS$')
_sign(DEFAULT, moneyed.MNT, prefix=u'₮')
_sign(DEFAULT, moneyed.VUV, prefix=u'VT')
_sign(DEFAULT, moneyed.KPW, prefix=u'₩')
_sign(DEFAULT, moneyed.KRW, prefix=u'₩')
_sign(DEFAULT, moneyed.JPY, prefix=u'¥')
_sign(DEFAULT, moneyed.CNY, prefix=u'¥')
_sign(DEFAULT, moneyed.PLN, prefix=u'zł')