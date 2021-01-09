# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from babel.numbers import LC_NUMERIC
from babel.numbers import format_currency as babel_format_currency


def format_money(money, format=None, locale=LC_NUMERIC, currency_digits=True,
                 format_type='standard', decimal_quantization=True):
    """
    See https://babel.pocoo.org/en/latest/api/numbers.html
    """
    return babel_format_currency(money.amount, money.currency.code,
                                 format=format, locale=locale, currency_digits=currency_digits,
                                 format_type=format_type, decimal_quantization=decimal_quantization)
