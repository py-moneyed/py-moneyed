from classes import *


def set_default_currency(code):
    global DEFAULT_CURRENCY_CODE
    DEFAULT_CURRENCY_CODE = get_currency(code)


class Money(Money):
    def __init__(self, amount=Decimal('0.0'), currency=None):
        if currency is None:
            currency = DEFAULT_CURRENCY_CODE
        super(Money, self).__init__(amount, currency)
