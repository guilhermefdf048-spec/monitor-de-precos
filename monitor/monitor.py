"""Lógica principal: verifica cada produto e decide se deve alertar."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from .config import Product
from .price import format_brl
from .scraper import extract_price, fetch_html
from .storage import PriceHistory


@dataclass
class CheckResult:
    product: Product
    price: Decimal | None = None
    previous: Decimal | None = None
    error: str | None = None

    @property
    def hit_target(self) -> bool:
        return self.price is not None and self.price <= self.product.target_price


def check_product(
    product: Product,
    history: PriceHistory,
    fetch: Callable[[str], str] = fetch_html,
) -> CheckResult:
    """Busca o preço atual, salva no histórico e devolve o resultado."""
    previous = history.last_price(product.name)
    try:
        price = extract_price(fetch(product.url), product.selector)
    except Exception as exc:  # erro de rede, seletor errado etc.
        return CheckResult(product, previous=previous, error=str(exc))

    history.add(product.name, price)
    return CheckResult(product, price=price, previous=previous)


def alert_message(result: CheckResult) -> str:
    p = result.product
    msg = (
        f"{p.name} está por {format_brl(result.price)} "
        f"(alvo: {format_brl(p.target_price)})"
    )
    if result.previous is not None and result.previous != result.price:
        msg += f" — antes: {format_brl(result.previous)}"
    return f"{msg}\n{p.url}"
