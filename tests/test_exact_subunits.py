from decimal import Decimal, Inexact, localcontext

import pytest

from moneyed import Money


@pytest.mark.parametrize(
    ("amount", "currency", "expected"),
    [
        ("123.45", "USD", 12345),
        ("123.456", "USD", 12345),
        ("-123.456", "USD", -12345),
        ("0.009", "USD", 0),
        ("-0.009", "USD", 0),
        ("123.4567", "BHD", 123456),
        ("123.456", "JPY", 123),
    ],
)
def test_subunits_are_independent_of_decimal_precision(
    amount: str, currency: str, expected: int
) -> None:
    money = Money(Decimal(amount), currency)
    with localcontext() as context:
        context.prec = 4
        assert money.get_amount_in_sub_unit() == expected


def test_exact_conversion_does_not_trigger_inexact_trap() -> None:
    money = Money("123.45", "USD")
    with localcontext() as context:
        context.prec = 4
        context.traps[Inexact] = True
        assert money.get_amount_in_sub_unit() == 12345
        assert not context.flags[Inexact]
