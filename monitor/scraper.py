"""Download das páginas e extração do preço."""

from decimal import Decimal

import requests
from bs4 import BeautifulSoup

from .price import parse_price

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; monitor-de-precos/1.0; "
        "+https://github.com/)"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def fetch_html(url: str, timeout: float = 15.0) -> str:
    """Baixa o HTML de uma página."""
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_price(html: str, selector: str) -> Decimal:
    """Encontra o elemento pelo seletor CSS e converte o texto em preço."""
    soup = BeautifulSoup(html, "html.parser")
    element = soup.select_one(selector)
    if element is None:
        raise ValueError(f"seletor {selector!r} não encontrado na página")

    # Alguns sites guardam o preço num atributo (ex.: <meta content="99.90">)
    text = element.get("content") or element.get_text(" ", strip=True)
    return parse_price(text)
