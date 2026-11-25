import pytest

from moneyed import get_currency
from moneyed.classes import CurrencyDoesNotExist


@pytest.mark.parametrize(
    ("numeric", "code"), [(8, "ALL"), (36, "AUD"), (52, "BBD"), (840, "USD")]
)
def test_integer_numeric_codes_match_padded_string_codes(
    numeric: int, code: str
) -> None:
    expected = get_currency(code)
    assert get_currency(iso=numeric) is expected
    assert get_currency(iso=f"{numeric:03d}") is expected


@pytest.mark.parametrize("numeric", [-1, 1000])
def test_unknown_numeric_codes_still_raise(numeric: int) -> None:
    with pytest.raises(CurrencyDoesNotExist):
        get_currency(iso=numeric)
