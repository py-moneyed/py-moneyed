import pytest

from moneyed import USD, Money


@pytest.fixture(autouse=True)
def _add_entities(doctest_namespace: dict[str, object]) -> None:
    """
    Inserts entities into doctest namespaces so that imports don't have to be added to
    all examples.
    https://docs.pytest.org/en/stable/doctest.html#doctest-namespace-fixture
    """
    doctest_namespace["Money"] = Money
    doctest_namespace["USD"] = USD
