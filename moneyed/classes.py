# -*- coding: utf-8 -*-

# flake8: NOQA
from .money import (DEFAULT_CURRENCY_CODE,
                    CURRENCIES,
                    CURRENCIES_BY_ISO,
                    PYTHON2,
                    Money,
                    MoneyComparisonError,
                    Currency,
                    CurrencyDoesNotExist,
                    add_currency,
                    get_currency,
                    force_decimal
                    )
from .loader import load_currencies


DEFAULT_CURRENCY = add_currency(DEFAULT_CURRENCY_CODE, '999', 'Default currency.', [])


load_currencies(locale='en_US')

# obslete currencies
load_currencies(['BYR', 'LTL', 'LVL', 'MRO', 'STD', 'TMM', 'VEF',
                 'XFO', 'XFU', 'ZMK', 'ZWD', 'ZWL'], locale='en_US')

# currencies not supported by babel
IMP = add_currency('IMP', 'Nil', 'Isle of Man Pound', ['ISLE OF MAN'])
TVD = add_currency('TVD', 'Nil', 'Tuvalu dollar', ['TUVALU'])
ZWN = add_currency('ZWN', '942', 'Zimbabwe dollar A/08', ['ZIMBABWE'])

globals().update(CURRENCIES)
