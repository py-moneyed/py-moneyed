from moneyed import Money, MoneyRange
from moneyed.l10n import format_money, format_money_range

one_million_bucks = Money("1000000", "USD")
one_million_eur = Money("1000000", "EUR")
one_million_bucks_to_two_million_bucks = MoneyRange(["1000000", "2000000"], "USD")
one_million_eur_to_two_million_eur = MoneyRange(["1000000", "2000000"], "EUR")


def test_format_money():
    assert format_money(one_million_bucks, locale="en_US") == "$1,000,000.00"
    assert format_money(one_million_eur, locale="en_US") == "€1,000,000.00"

def test_format_money_range():
    assert format_money_range(one_million_bucks_to_two_million_bucks, locale="en_US") == "$1,000,000.00 to $2,000,000.00"
    assert format_money_range(one_million_eur_to_two_million_eur, locale="en_US") == "€1,000,000.00 to €2,000,000.00"


# Test a few things are being passed on. But don't test everything, it is tested in Babel


def test_format_money_decimal_quantization():
    assert (
        format_money(Money("2.0123", "USD"), locale="en_US", decimal_quantization=False)
        == "$2.0123"
    )


def test_format_money_range_decimal_quantization():
    amount = ["10.4567", "20.0123"]
    assert (
        format_money_range(MoneyRange(amount, "USD"), locale="en_US", decimal_quantization=False)
        == "$10.4567 to $20.0123"
    )
