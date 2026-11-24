import json
from decimal import Decimal
from pathlib import Path

import pytest

from monitor.config import Product, load_products
from monitor.monitor import alert_message, check_product
from monitor.scraper import extract_price
from monitor.storage import PriceHistory

HTML = (Path(__file__).parent / "fixtures" / "produto.html").read_text(encoding="utf-8")


@pytest.fixture
def history():
    h = PriceHistory(":memory:")
    yield h
    h.close()


def make_product(target="300", selector="meta[itemprop=price]"):
    return Product("Fone XYZ", "https://loja.exemplo/fone", selector, Decimal(target))


def test_extract_price_from_text():
    assert extract_price(HTML, ".preco-atual") == Decimal("1249.90")


def test_extract_price_from_meta_content():
    assert extract_price(HTML, "meta[itemprop=price]") == Decimal("249.90")


def test_extract_price_missing_selector():
    with pytest.raises(ValueError, match="não encontrado"):
        extract_price(HTML, ".nao-existe")


def test_check_product_hits_target_and_saves(history):
    result = check_product(make_product(target="300"), history, fetch=lambda url: HTML)
    assert result.error is None
    assert result.price == Decimal("249.90")
    assert result.hit_target
    assert history.last_price("Fone XYZ") == Decimal("249.90")


def test_check_product_above_target(history):
    result = check_product(make_product(target="200"), history, fetch=lambda url: HTML)
    assert not result.hit_target


def test_check_product_handles_errors(history):
    def broken_fetch(url):
        raise ConnectionError("sem internet")

    result = check_product(make_product(), history, fetch=broken_fetch)
    assert result.error == "sem internet"
    assert history.last_price("Fone XYZ") is None


def test_alert_message_shows_previous_price(history):
    history.add("Fone XYZ", Decimal("299.90"))
    result = check_product(make_product(), history, fetch=lambda url: HTML)
    msg = alert_message(result)
    assert "R$ 249,90" in msg
    assert "antes: R$ 299,90" in msg
    assert history.lowest_price("Fone XYZ") == Decimal("249.90")


def test_load_products(tmp_path):
    file = tmp_path / "produtos.json"
    file.write_text(
        json.dumps({"produtos": [{"nome": "A", "url": "u", "seletor": ".p", "preco_alvo": 10.5}]}),
        encoding="utf-8",
    )
    [product] = load_products(file)
    assert product.target_price == Decimal("10.5")


def test_load_products_missing_field(tmp_path):
    file = tmp_path / "produtos.json"
    file.write_text(json.dumps({"produtos": [{"nome": "A"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="url"):
        load_products(file)
