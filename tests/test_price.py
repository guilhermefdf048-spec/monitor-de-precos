from decimal import Decimal

import pytest

from monitor.price import format_brl, parse_price


@pytest.mark.parametrize(
    "text, expected",
    [
        ("R$ 1.299,90", "1299.90"),
        ("R$ 49,90", "49.90"),
        ("Por: R$ 10.000", "10000"),
        ("$1,299.90", "1299.90"),
        ("249.90", "249.90"),
        ("R$ 1 299,90", "1299.90"),
        ("12x de R$ 99,00", "12"),  # pega o primeiro número
    ],
)
def test_parse_price(text, expected):
    assert parse_price(text) == Decimal(expected)


@pytest.mark.parametrize("text", ["", "Indisponível", "R$ --"])
def test_parse_price_invalid(text):
    with pytest.raises(ValueError):
        parse_price(text)


def test_format_brl():
    assert format_brl(Decimal("1299.9")) == "R$ 1.299,90"
    assert format_brl(Decimal("5")) == "R$ 5,00"
