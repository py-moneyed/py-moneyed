# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from moneyed import Money
from moneyed.l10n import format_money

one_million_bucks = Money('1000000', 'USD')
one_million_eur = Money('1000000', 'EUR')


def test_format_money():
    assert format_money(one_million_bucks, locale='en_US') == '$1,000,000.00'
    assert format_money(one_million_eur, locale='en_US') == '€1,000,000.00'


# Test a few things are being passed on. But don't test everything, it is tested in Babel


def test_format_money_decimal_quantization():
    assert format_money(Money('2.0123', 'USD'), locale='en_US', decimal_quantization=False) == '$2.0123'
