# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re

from babel.numbers import format_currency as babel_format_currency, LC_NUMERIC
from babel.core import Locale


def format_currency(money, *args, **kwargs):
    return babel_format_currency(money.amount, money.currency.code, *args, **kwargs)


DECIMAL_PLACES_REGEX = re.compile(r'\.0*')


def format_money(
    money,
    include_symbol=True,
    locale=LC_NUMERIC,
    decimal_places=None,
    rounding_method=None,
):
    # FIXME: rounding_method is doing nothing
    locale = Locale.parse(locale)
    format = locale.currency_formats['standard'].pattern
    if not include_symbol:
        format = format.replace('¤', '').strip()
    if decimal_places is not None:
        zeroes = '0' * decimal_places
        format = re.sub(DECIMAL_PLACES_REGEX, '.' + zeroes, format)

    return format_currency(
        money,
        format=format,
        locale=locale,
        currency_digits=False,
        decimal_quantization=True,
    )
